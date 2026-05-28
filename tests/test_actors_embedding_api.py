#!/usr/bin/env python3
"""
Tests for apis/actors_embedding_api.py

All external dependencies (EmbeddingSearchEngine, MLPipelineManager) are
mocked via sys.modules so the Flask app can be imported and exercised without
real ML libraries being installed.
"""

import sys
import types
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Stub out external dependencies before importing the module
# ---------------------------------------------------------------------------

def _make_result(id_="doc1", path="/data/file.md", chunk_index=0, similarity=0.85):
    return {
        "metadata": {"id": id_, "path": path, "chunk_index": chunk_index},
        "similarity": similarity,
    }


# Embedding search stub
_emb_stub = types.ModuleType("embedding_search")


class _FakeEmbeddingSearchEngine:
    def __init__(self, *a, **kw):
        self.embeddings_data = [
            {"vector": [0.1, 0.2]},
            {"vector": [0.3, 0.4]},
        ]
        self.metadata = [
            {"id": "doc1", "path": "/data/file1.md", "chunk_index": 0},
            {"id": "doc2", "path": "/data/file2.md", "chunk_index": 1},
        ]

    def load_embeddings(self):
        pass

    def get_statistics(self):
        return {"total_embeddings": 2, "average_similarity": 0.75, "last_updated": "now"}

    def search_by_text(self, query, top_k):
        return [_make_result()][:top_k]

    def find_similar_to_id(self, embedding_id, top_k):
        return [_make_result()][:top_k]

    def get_embedding_by_id(self, embedding_id):
        if embedding_id == "missing":
            return None
        return {
            "metadata": {
                "id": embedding_id,
                "path": "/data/file.md",
                "chunk_index": 0,
                "text_sha256": "abc123",
            },
            "embedding_data": {"embedding": [0.1, 0.2, 0.3]},
        }

    def cluster_embeddings(self, n_clusters):
        return {
            "clusters": {0: [_make_result()]},
            "explained_variance_ratio": [0.5],
        }


_emb_stub.EmbeddingSearchEngine = _FakeEmbeddingSearchEngine
sys.modules["embedding_search"] = _emb_stub

# ML pipeline stub
_ml_stub = types.ModuleType("ml_pipeline_integration")


class _FakeMLPipelineManager:
    async def initialize(self):
        pass

    async def get_pipeline_health(self):
        return {"is_active": True, "total_models": 2}


_ml_stub.MLPipelineManager = _FakeMLPipelineManager
_ml_stub.MLEnhancedSpeechToTradingSystem = MagicMock
sys.modules["ml_pipeline_integration"] = _ml_stub

# Add apis/ to path so the module can be imported directly
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "apis"))

import actors_embedding_api as api_module
from actors_embedding_api import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def no_engine(client):
    """search_engine is None (uninitialised state)."""
    with patch.object(api_module, "search_engine", None):
        yield client


@pytest.fixture()
def engine_up(client):
    """search_engine is a functional fake, ml_pipeline is None."""
    with patch.object(api_module, "search_engine", _FakeEmbeddingSearchEngine()):
        yield client


@pytest.fixture()
def ml_up(client):
    """Both search_engine and ml_pipeline are functional fakes."""
    with (
        patch.object(api_module, "search_engine", _FakeEmbeddingSearchEngine()),
        patch.object(api_module, "ml_pipeline", _FakeMLPipelineManager()),
    ):
        yield client


# ===========================================================================
# /health
# ===========================================================================

class TestHealthEndpoint:
    def test_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_response_structure(self, client):
        data = client.get("/health").get_json()
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert "embeddings_loaded" in data
        assert "ml_pipeline_active" in data

    def test_embeddings_loaded_false_when_no_engine(self, no_engine):
        data = no_engine.get("/health").get_json()
        assert data["embeddings_loaded"] is False

    def test_embeddings_loaded_true_when_engine_up(self, engine_up):
        data = engine_up.get("/health").get_json()
        assert data["embeddings_loaded"] is True

    def test_ml_pipeline_active_true_when_ml_up(self, ml_up):
        data = ml_up.get("/health").get_json()
        assert data["ml_pipeline_active"] is True


# ===========================================================================
# /stats
# ===========================================================================

class TestStatsEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.get("/stats")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_200_when_engine_up(self, engine_up):
        resp = engine_up.get("/stats")
        assert resp.status_code == 200
        assert "total_embeddings" in resp.get_json()


# ===========================================================================
# /search
# ===========================================================================

class TestSearchEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.post("/search", json={"query": "test"}, content_type="application/json")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_400_when_empty_query(self, engine_up):
        resp = engine_up.post("/search", json={"query": ""}, content_type="application/json")
        assert resp.status_code == 400

    def test_returns_200_with_valid_query(self, engine_up):
        resp = engine_up.post(
            "/search",
            json={"query": "actor data", "top_k": 5},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["query"] == "actor data"
        assert "results" in data
        assert "total_results" in data
        assert "search_time_ms" in data

    def test_result_fields(self, engine_up):
        resp = engine_up.post("/search", json={"query": "test"}, content_type="application/json")
        data = resp.get_json()
        assert data["total_results"] >= 0
        if data["results"]:
            r = data["results"][0]
            for field in ("id", "path", "chunk_index", "similarity", "filename"):
                assert field in r

    def test_default_top_k(self, engine_up):
        resp = engine_up.post("/search", json={"query": "test"}, content_type="application/json")
        assert resp.status_code == 200


# ===========================================================================
# /similar/<id>
# ===========================================================================

class TestSimilarEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.get("/similar/doc1")
        assert resp.status_code == 500

    def test_returns_200_when_engine_up(self, engine_up):
        resp = engine_up.get("/similar/doc1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["target_id"] == "doc1"
        assert "results" in data
        assert "total_results" in data
        assert "search_time_ms" in data

    def test_result_fields(self, engine_up):
        resp = engine_up.get("/similar/doc1")
        data = resp.get_json()
        if data["results"]:
            r = data["results"][0]
            for field in ("id", "path", "chunk_index", "similarity", "filename"):
                assert field in r

    def test_respects_top_k_param(self, engine_up):
        resp = engine_up.get("/similar/doc1?top_k=1")
        assert resp.status_code == 200


# ===========================================================================
# /embedding/<id>
# ===========================================================================

class TestGetEmbeddingEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.get("/embedding/doc1")
        assert resp.status_code == 500

    def test_returns_200_when_found(self, engine_up):
        resp = engine_up.get("/embedding/doc1")
        assert resp.status_code == 200
        data = resp.get_json()
        for field in ("id", "path", "chunk_index", "text_sha256", "embedding_dimension"):
            assert field in data

    def test_embedding_dimension_is_int(self, engine_up):
        data = engine_up.get("/embedding/doc1").get_json()
        assert isinstance(data["embedding_dimension"], int)

    def test_returns_404_when_not_found(self, engine_up):
        resp = engine_up.get("/embedding/missing")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


# ===========================================================================
# /cluster
# ===========================================================================

class TestClusterEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.post("/cluster", json={"n_clusters": 5}, content_type="application/json")
        assert resp.status_code == 500

    def test_returns_200_when_engine_up(self, engine_up):
        resp = engine_up.post("/cluster", json={"n_clusters": 3}, content_type="application/json")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "n_clusters" in data
        assert "clusters" in data
        assert "cluster_time_ms" in data

    def test_cluster_structure(self, engine_up):
        data = engine_up.post("/cluster", json={}, content_type="application/json").get_json()
        for cluster_info in data["clusters"].values():
            assert "size" in cluster_info
            assert "sample_files" in cluster_info

    def test_cluster_failure_returns_500(self, client):
        fake_engine = _FakeEmbeddingSearchEngine()
        fake_engine.cluster_embeddings = lambda n: None
        with patch.object(api_module, "search_engine", fake_engine):
            resp = client.post("/cluster", json={"n_clusters": 3}, content_type="application/json")
        assert resp.status_code == 500


# ===========================================================================
# /recommendations
# ===========================================================================

class TestRecommendationsEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.post(
            "/recommendations", json={"query": "test"}, content_type="application/json"
        )
        assert resp.status_code == 500

    def test_returns_400_when_empty_query(self, engine_up):
        resp = engine_up.post(
            "/recommendations", json={"query": ""}, content_type="application/json"
        )
        assert resp.status_code == 400

    def test_returns_200_with_valid_query(self, engine_up):
        resp = engine_up.post(
            "/recommendations",
            json={"query": "actor data", "top_k": 3},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["query"] == "actor data"
        assert "recommendations" in data
        assert "total_recommendations" in data

    def test_recommendations_deduplicated_by_file(self, engine_up):
        resp = engine_up.post(
            "/recommendations", json={"query": "test"}, content_type="application/json"
        )
        data = resp.get_json()
        filenames = [r["path"] for r in data["recommendations"]]
        assert len(filenames) == len(set(filenames))


# ===========================================================================
# /explore
# ===========================================================================

class TestExploreEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.get("/explore")
        assert resp.status_code == 500

    def test_returns_200_when_engine_up(self, engine_up):
        resp = engine_up.get("/explore")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "samples" in data
        assert "total_embeddings" in data

    def test_sample_fields(self, engine_up):
        data = engine_up.get("/explore").get_json()
        for sample in data["samples"]:
            for field in ("id", "path", "chunk_index", "filename"):
                assert field in sample

    def test_respects_limit_param(self, engine_up):
        data = engine_up.get("/explore?limit=1").get_json()
        assert len(data["samples"]) <= 1

    def test_total_embeddings_matches_engine(self, engine_up):
        data = engine_up.get("/explore").get_json()
        assert data["total_embeddings"] == 2


# ===========================================================================
# /ml/search
# ===========================================================================

class TestMlSearchEndpoint:
    def test_returns_500_when_no_engine(self, no_engine):
        resp = no_engine.post(
            "/ml/search", json={"query": "test"}, content_type="application/json"
        )
        assert resp.status_code == 500

    def test_returns_500_when_no_ml_pipeline(self, engine_up):
        resp = engine_up.post(
            "/ml/search", json={"query": "test"}, content_type="application/json"
        )
        assert resp.status_code == 500

    def test_returns_400_when_empty_query(self, ml_up):
        resp = ml_up.post(
            "/ml/search", json={"query": ""}, content_type="application/json"
        )
        assert resp.status_code == 400

    def test_returns_200_with_ml_enhancement_off(self, ml_up):
        resp = ml_up.post(
            "/ml/search",
            json={"query": "actor", "top_k": 5, "ml_enhancement": False},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["query"] == "actor"
        assert "results" in data
        assert "total_results" in data
        assert "search_time_ms" in data
        assert "ml_enhanced" in data
        assert data["ml_enhanced"] is False

    def test_result_fields_with_ml_enhancement_off(self, ml_up):
        resp = ml_up.post(
            "/ml/search",
            json={"query": "test", "ml_enhancement": False},
            content_type="application/json",
        )
        data = resp.get_json()
        if data["results"]:
            r = data["results"][0]
            for field in ("id", "path", "chunk_index", "similarity", "filename", "ml_enhanced"):
                assert field in r


# ===========================================================================
# /ml/status
# ===========================================================================

class TestMlStatusEndpoint:
    def test_returns_500_when_no_ml_pipeline(self, client):
        with patch.object(api_module, "ml_pipeline", None):
            resp = client.get("/ml/status")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_200_when_ml_pipeline_up(self, ml_up):
        resp = ml_up.get("/ml/status")
        assert resp.status_code == 200


# ===========================================================================
# Error handlers
# ===========================================================================

class TestErrorHandlers:
    def test_404_handler(self, client):
        resp = client.get("/nonexistent_endpoint_xyz")
        assert resp.status_code == 404
        assert "error" in resp.get_json()
