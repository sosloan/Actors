"""
Tests for apis/geospatial_api.py

Tests all Flask endpoints of the Geospatial API using mocked
GeospatialEngine and GDAL dependencies.
"""

import sys
import os
import types
import json
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

# ---------------------------------------------------------------------------
# Inject mock modules so the API can be imported without real GDAL
# ---------------------------------------------------------------------------

# Mock rasterio
_mock_rasterio = types.ModuleType("rasterio")
_mock_rasterio.open = MagicMock()
sys.modules.setdefault("rasterio", _mock_rasterio)

# Mock osgeo / gdal
_mock_osgeo = types.ModuleType("osgeo")
_mock_gdal = types.ModuleType("osgeo.gdal")
_mock_gdal.__version__ = "3.8.3"
_mock_gdal.UseExceptions = MagicMock()
_mock_osgeo.gdal = _mock_gdal
sys.modules.setdefault("osgeo", _mock_osgeo)
sys.modules.setdefault("osgeo.gdal", _mock_gdal)
sys.modules.setdefault("osgeo.ogr", types.ModuleType("osgeo.ogr"))
sys.modules.setdefault("osgeo.osr", types.ModuleType("osgeo.osr"))

# Mock geopandas
_mock_geopandas = types.ModuleType("geopandas")
sys.modules.setdefault("geopandas", _mock_geopandas)

# Mock shapely
_mock_shapely = types.ModuleType("shapely")
_mock_shapely_geo = types.ModuleType("shapely.geometry")
_mock_shapely_geo.Point = MagicMock()
_mock_shapely_geo.Polygon = MagicMock()
_mock_shapely_geo.box = MagicMock()
sys.modules.setdefault("shapely", _mock_shapely)
sys.modules.setdefault("shapely.geometry", _mock_shapely_geo)

# Mock rasterio sub-modules
_mock_rasterio_warp = types.ModuleType("rasterio.warp")
sys.modules.setdefault("rasterio.warp", _mock_rasterio_warp)

# Build a fake geospatial_engine module so geospatial_api can import it
_mock_geo_engine_mod = types.ModuleType("core.geospatial_engine")

class _FakeRasterMetadata:
    def to_dict(self):
        return {
            "width": 50,
            "height": 50,
            "bands": 1,
            "projection": "EPSG:4326",
            "geotransform": [0, 1, 0, 0, 0, 1],
            "bounds": [-180, -90, 180, 90],
            "nodata_value": None
        }

class _FakeVectorMetadata:
    def to_dict(self):
        return {
            "feature_count": 3,
            "geometry_type": "Point",
            "projection": "EPSG:4326",
            "bounds": [-130, 30, -70, 50],
            "fields": ["name", "population", "geometry"]
        }

import numpy as np

class _FakeGeospatialEngine:
    """Minimal synchronous-friendly fake of GeospatialEngine"""
    def __init__(self, cache_dir=None):
        self._raster_cache = {}
        self._vector_cache = {}
        self.cache_dir = cache_dir

    async def initialize(self):
        pass

    async def load_raster(self, file_path, cache_key=None):
        data = np.random.rand(50, 50).astype(np.float32)
        return {
            "data": data,
            "metadata": _FakeRasterMetadata(),
            "stats": {"min": 0.0, "max": 1.0, "mean": 0.5, "std": 0.2}
        }

    async def read_raster_at_point(self, file_path, lon, lat):
        return 0.42

    async def compute_ndvi(self, red_band_path, nir_band_path):
        ndvi = np.random.rand(50, 50).astype(np.float32)
        return {
            "ndvi": ndvi,
            "metadata": _FakeRasterMetadata(),
            "stats": {
                "min": -0.1,
                "max": 0.9,
                "mean": 0.55,
                "vegetation_cover_pct": 60.0
            }
        }

    async def compute_raster_statistics(self, file_path, polygon=None):
        return {
            "min": 0.0,
            "max": 1.0,
            "mean": 0.5,
            "median": 0.5,
            "std": 0.2,
            "percentile_25": 0.3,
            "percentile_75": 0.7
        }

    async def load_vector(self, file_path, cache_key=None):
        return {
            "gdf": MagicMock(),
            "metadata": _FakeVectorMetadata(),
            "preview": [
                {"name": "SF", "population": 874961},
                {"name": "LA", "population": 3979576},
                {"name": "NY", "population": 8336817}
            ]
        }

    async def query_vector_by_location(self, file_path, lon, lat, buffer_meters=0):
        return [{"name": "SF", "population": 874961}]

    async def query_vector_by_bbox(self, file_path, bbox):
        return [
            {"name": "SF", "population": 874961},
            {"name": "LA", "population": 3979576}
        ]

    async def get_elevation_profile(self, dem_path, points):
        return [{"lon": lon, "lat": lat, "elevation": 100.0} for lon, lat in points]

    def get_cache_info(self):
        return {
            "raster_cache": list(self._raster_cache.keys()),
            "vector_cache": list(self._vector_cache.keys()),
            "cache_dir": str(self.cache_dir)
        }

    def clear_cache(self):
        self._raster_cache.clear()
        self._vector_cache.clear()


_mock_geo_engine_mod.GeospatialEngine = _FakeGeospatialEngine
_mock_geo_engine_mod.GDAL_AVAILABLE = True
_mock_geo_engine_mod.RasterMetadata = _FakeRasterMetadata
_mock_geo_engine_mod.VectorMetadata = _FakeVectorMetadata

# Register fake modules before the API is imported
sys.modules["core.geospatial_engine"] = _mock_geo_engine_mod

# Build fake database.config
_mock_db_config_mod = types.ModuleType("database.config")

class _FakeGeospatialConfig:
    cache_dir = "/tmp/geospatial_cache"
    max_raster_size_mb = 500
    enable_caching = True
    default_projection = "EPSG:4326"

_mock_db_config_mod.GeospatialConfig = _FakeGeospatialConfig
sys.modules["database.config"] = _mock_db_config_mod

# Also ensure parent packages exist in sys.modules
sys.modules.setdefault("core", types.ModuleType("core"))
sys.modules.setdefault("database", types.ModuleType("database"))

# Now import the API
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "apis"))
import geospatial_api as api_module
from geospatial_api import app


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_engine():
    """Reset engine global and install a fresh fake engine before each test."""
    api_module.engine = _FakeGeospatialEngine(cache_dir="/tmp/geospatial_cache")
    yield
    api_module.engine = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_RASTER = "/tmp/fake_raster.tif"
_FAKE_VECTOR = "/tmp/fake_vector.geojson"
_FAKE_DEM    = "/tmp/fake_dem.tif"
_FAKE_RED    = "/tmp/fake_red.tif"
_FAKE_NIR    = "/tmp/fake_nir.tif"


def _post(client, url, body):
    return client.post(url, data=json.dumps(body), content_type="application/json")


# ---------------------------------------------------------------------------
# GET /api/geo  (API info)
# ---------------------------------------------------------------------------

class TestApiInfo:
    def test_returns_200(self, client):
        assert client.get("/api/geo").status_code == 200

    def test_response_has_name(self, client):
        data = client.get("/api/geo").get_json()
        assert data["name"] == "ACTORS Geospatial API"

    def test_response_has_endpoints(self, client):
        data = client.get("/api/geo").get_json()
        assert "endpoints" in data
        assert "raster" in data["endpoints"]
        assert "vector" in data["endpoints"]

    def test_response_has_gdal_flag(self, client):
        data = client.get("/api/geo").get_json()
        assert "gdal_available" in data

    def test_response_has_use_cases(self, client):
        data = client.get("/api/geo").get_json()
        assert "use_cases" in data
        assert len(data["use_cases"]) > 0


# ---------------------------------------------------------------------------
# GET /api/geo/status
# ---------------------------------------------------------------------------

class TestStatus:
    def test_returns_200(self, client):
        assert client.get("/api/geo/status").status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/geo/status").get_json()
        assert data["status"] == "operational"
        assert "gdal_available" in data
        assert "cache" in data
        assert "config" in data

    def test_config_fields(self, client):
        data = client.get("/api/geo/status").get_json()
        cfg = data["config"]
        assert "cache_dir" in cfg
        assert "max_raster_size_mb" in cfg
        assert "enable_caching" in cfg
        assert "default_projection" in cfg

    def test_status_error_propagates(self, client):
        api_module.engine = MagicMock()
        api_module.engine.get_cache_info.side_effect = RuntimeError("boom")
        resp = client.get("/api/geo/status")
        assert resp.status_code == 500
        assert "error" in resp.get_json()


# ---------------------------------------------------------------------------
# POST /api/geo/cache/clear
# ---------------------------------------------------------------------------

class TestClearCache:
    def test_returns_200(self, client):
        resp = _post(client, "/api/geo/cache/clear", {})
        assert resp.status_code == 200

    def test_response_message(self, client):
        data = _post(client, "/api/geo/cache/clear", {}).get_json()
        assert data["status"] == "success"
        assert "Cache cleared" in data["message"]

    def test_clears_when_no_engine(self, client):
        api_module.engine = None
        resp = _post(client, "/api/geo/cache/clear", {})
        assert resp.status_code == 200

    def test_error_propagates(self, client):
        api_module.engine = MagicMock()
        api_module.engine.clear_cache.side_effect = RuntimeError("oops")
        resp = _post(client, "/api/geo/cache/clear", {})
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/raster/load
# ---------------------------------------------------------------------------

class TestLoadRaster:
    def test_missing_file_path_returns_400(self, client):
        resp = _post(client, "/api/geo/raster/load", {})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_nonexistent_file_returns_404(self, client):
        resp = _post(client, "/api/geo/raster/load", {"file_path": "/no/such/file.tif"})
        assert resp.status_code == 404

    def test_valid_file_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/load", {"file_path": _FAKE_RASTER})
        assert resp.status_code == 200

    def test_response_structure(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/raster/load", {"file_path": _FAKE_RASTER}).get_json()
        assert "metadata" in data
        assert "stats" in data
        assert "data_shape" in data

    def test_cached_flag_true_when_cache_key_provided(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/raster/load", {
                "file_path": _FAKE_RASTER,
                "cache_key": "mykey"
            }).get_json()
        assert data["cached"] is True

    def test_cached_flag_false_when_no_cache_key(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/raster/load", {"file_path": _FAKE_RASTER}).get_json()
        assert data["cached"] is False

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.load_raster = AsyncMock(side_effect=RuntimeError("engine error"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/load", {"file_path": _FAKE_RASTER})
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/raster/point-query
# ---------------------------------------------------------------------------

class TestRasterPointQuery:
    def test_missing_params_returns_400(self, client):
        resp = _post(client, "/api/geo/raster/point-query", {"file_path": _FAKE_RASTER})
        assert resp.status_code == 400

    def test_nonexistent_file_returns_404(self, client):
        resp = _post(client, "/api/geo/raster/point-query", {
            "file_path": "/no/such/file.tif", "lon": 0.0, "lat": 0.0
        })
        assert resp.status_code == 404

    def test_valid_query_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/point-query", {
                "file_path": _FAKE_RASTER, "lon": -122.4, "lat": 37.7
            })
        assert resp.status_code == 200

    def test_response_contains_coordinates_and_value(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/raster/point-query", {
                "file_path": _FAKE_RASTER, "lon": -122.4, "lat": 37.7
            }).get_json()
        assert data["lon"] == -122.4
        assert data["lat"] == 37.7
        assert "value" in data

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.read_raster_at_point = AsyncMock(side_effect=RuntimeError("err"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/point-query", {
                "file_path": _FAKE_RASTER, "lon": 0.0, "lat": 0.0
            })
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/raster/ndvi
# ---------------------------------------------------------------------------

class TestComputeNDVI:
    def test_missing_bands_returns_400(self, client):
        resp = _post(client, "/api/geo/raster/ndvi", {"red_band": _FAKE_RED})
        assert resp.status_code == 400

    def test_missing_red_band_file_returns_404(self, client):
        with patch("os.path.exists", side_effect=lambda p: p == _FAKE_NIR):
            resp = _post(client, "/api/geo/raster/ndvi", {
                "red_band": "/no/red.tif", "nir_band": _FAKE_NIR
            })
        assert resp.status_code == 404

    def test_missing_nir_band_file_returns_404(self, client):
        with patch("os.path.exists", side_effect=lambda p: p == _FAKE_RED):
            resp = _post(client, "/api/geo/raster/ndvi", {
                "red_band": _FAKE_RED, "nir_band": "/no/nir.tif"
            })
        assert resp.status_code == 404

    def test_valid_request_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/ndvi", {
                "red_band": _FAKE_RED, "nir_band": _FAKE_NIR
            })
        assert resp.status_code == 200

    def test_response_structure(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/raster/ndvi", {
                "red_band": _FAKE_RED, "nir_band": _FAKE_NIR
            }).get_json()
        assert "metadata" in data
        assert "stats" in data
        assert "ndvi_shape" in data
        assert "interpretation" in data

    def test_interpretation_health_rating_present(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/raster/ndvi", {
                "red_band": _FAKE_RED, "nir_band": _FAKE_NIR
            }).get_json()
        interp = data["interpretation"]
        assert "health_rating" in interp
        assert interp["health_rating"] in ("Excellent", "Good", "Fair", "Poor")

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.compute_ndvi = AsyncMock(side_effect=RuntimeError("ndvi error"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/ndvi", {
                "red_band": _FAKE_RED, "nir_band": _FAKE_NIR
            })
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/raster/statistics
# ---------------------------------------------------------------------------

class TestRasterStatistics:
    def test_missing_file_path_returns_400(self, client):
        resp = _post(client, "/api/geo/raster/statistics", {})
        assert resp.status_code == 400

    def test_nonexistent_file_returns_404(self, client):
        resp = _post(client, "/api/geo/raster/statistics", {"file_path": "/no/file.tif"})
        assert resp.status_code == 404

    def test_valid_request_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/statistics", {"file_path": _FAKE_RASTER})
        assert resp.status_code == 200

    def test_response_contains_statistics(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/raster/statistics", {"file_path": _FAKE_RASTER}).get_json()
        for key in ("min", "max", "mean", "median", "std", "percentile_25", "percentile_75"):
            assert key in data

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.compute_raster_statistics = AsyncMock(side_effect=RuntimeError("stats err"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/raster/statistics", {"file_path": _FAKE_RASTER})
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/vector/load
# ---------------------------------------------------------------------------

class TestLoadVector:
    def test_missing_file_path_returns_400(self, client):
        resp = _post(client, "/api/geo/vector/load", {})
        assert resp.status_code == 400

    def test_nonexistent_file_returns_404(self, client):
        resp = _post(client, "/api/geo/vector/load", {"file_path": "/no/file.geojson"})
        assert resp.status_code == 404

    def test_valid_request_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/vector/load", {"file_path": _FAKE_VECTOR})
        assert resp.status_code == 200

    def test_response_structure(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/vector/load", {"file_path": _FAKE_VECTOR}).get_json()
        assert "metadata" in data
        assert "preview" in data
        assert "cached" in data

    def test_cached_flag_true_with_cache_key(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/vector/load", {
                "file_path": _FAKE_VECTOR, "cache_key": "vkey"
            }).get_json()
        assert data["cached"] is True

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.load_vector = AsyncMock(side_effect=RuntimeError("vec err"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/vector/load", {"file_path": _FAKE_VECTOR})
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/vector/location-query
# ---------------------------------------------------------------------------

class TestVectorLocationQuery:
    def test_missing_params_returns_400(self, client):
        resp = _post(client, "/api/geo/vector/location-query", {"file_path": _FAKE_VECTOR})
        assert resp.status_code == 400

    def test_nonexistent_file_returns_404(self, client):
        resp = _post(client, "/api/geo/vector/location-query", {
            "file_path": "/no/file.geojson", "lon": -122.4, "lat": 37.7
        })
        assert resp.status_code == 404

    def test_valid_request_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/vector/location-query", {
                "file_path": _FAKE_VECTOR, "lon": -122.4, "lat": 37.7
            })
        assert resp.status_code == 200

    def test_response_structure(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/vector/location-query", {
                "file_path": _FAKE_VECTOR, "lon": -122.4, "lat": 37.7
            }).get_json()
        assert "query" in data
        assert "feature_count" in data
        assert "features" in data

    def test_buffer_meters_passed_through(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/vector/location-query", {
                "file_path": _FAKE_VECTOR, "lon": -122.4, "lat": 37.7, "buffer_meters": 500
            }).get_json()
        assert data["query"]["buffer_meters"] == 500

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.query_vector_by_location = AsyncMock(side_effect=RuntimeError("loc err"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/vector/location-query", {
                "file_path": _FAKE_VECTOR, "lon": 0.0, "lat": 0.0
            })
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/vector/bbox-query
# ---------------------------------------------------------------------------

class TestVectorBboxQuery:
    def test_missing_params_returns_400(self, client):
        resp = _post(client, "/api/geo/vector/bbox-query", {"file_path": _FAKE_VECTOR})
        assert resp.status_code == 400

    def test_invalid_bbox_length_returns_400(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/vector/bbox-query", {
                "file_path": _FAKE_VECTOR, "bbox": [-122.5, 37.7]
            })
        assert resp.status_code == 400

    def test_nonexistent_file_returns_404(self, client):
        resp = _post(client, "/api/geo/vector/bbox-query", {
            "file_path": "/no/file.geojson", "bbox": [-125, 32, -115, 40]
        })
        assert resp.status_code == 404

    def test_valid_request_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/vector/bbox-query", {
                "file_path": _FAKE_VECTOR, "bbox": [-125, 32, -115, 40]
            })
        assert resp.status_code == 200

    def test_response_structure(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/vector/bbox-query", {
                "file_path": _FAKE_VECTOR, "bbox": [-125, 32, -115, 40]
            }).get_json()
        assert "query" in data
        assert "feature_count" in data
        assert "features" in data

    def test_bbox_echoed_in_response(self, client):
        bbox = [-125, 32, -115, 40]
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/vector/bbox-query", {
                "file_path": _FAKE_VECTOR, "bbox": bbox
            }).get_json()
        assert data["query"]["bbox"] == bbox

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.query_vector_by_bbox = AsyncMock(side_effect=RuntimeError("bbox err"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/vector/bbox-query", {
                "file_path": _FAKE_VECTOR, "bbox": [-125, 32, -115, 40]
            })
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/geo/analytics/elevation-profile
# ---------------------------------------------------------------------------

class TestElevationProfile:
    def test_missing_dem_path_returns_400(self, client):
        resp = _post(client, "/api/geo/analytics/elevation-profile", {
            "points": [[0, 0], [10, 10]]
        })
        assert resp.status_code == 400

    def test_missing_points_returns_400(self, client):
        resp = _post(client, "/api/geo/analytics/elevation-profile", {
            "dem_path": _FAKE_DEM, "points": []
        })
        assert resp.status_code == 400

    def test_nonexistent_dem_returns_404(self, client):
        resp = _post(client, "/api/geo/analytics/elevation-profile", {
            "dem_path": "/no/dem.tif", "points": [[0, 0], [1, 1]]
        })
        assert resp.status_code == 404

    def test_valid_request_returns_200(self, client):
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/analytics/elevation-profile", {
                "dem_path": _FAKE_DEM, "points": [[0, 0], [10, 10], [20, 20]]
            })
        assert resp.status_code == 200

    def test_response_has_profile_and_metrics(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/analytics/elevation-profile", {
                "dem_path": _FAKE_DEM, "points": [[0, 0], [10, 10], [20, 20]]
            }).get_json()
        assert "profile" in data
        assert "metrics" in data

    def test_profile_has_correct_number_of_points(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/analytics/elevation-profile", {
                "dem_path": _FAKE_DEM, "points": [[0, 0], [10, 10], [20, 20]]
            }).get_json()
        assert len(data["profile"]) == 3

    def test_profile_point_structure(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/analytics/elevation-profile", {
                "dem_path": _FAKE_DEM, "points": [[5, 10]]
            }).get_json()
        point = data["profile"][0]
        assert "lon" in point
        assert "lat" in point
        assert "elevation" in point

    def test_metrics_contain_elevation_stats(self, client):
        with patch("os.path.exists", return_value=True):
            data = _post(client, "/api/geo/analytics/elevation-profile", {
                "dem_path": _FAKE_DEM, "points": [[0, 0], [10, 10]]
            }).get_json()
        metrics = data["metrics"]
        assert "min_elevation" in metrics
        assert "max_elevation" in metrics
        assert "elevation_gain" in metrics
        assert "elevation_loss" in metrics

    def test_engine_error_returns_500(self, client):
        api_module.engine = MagicMock()
        api_module.engine.get_elevation_profile = AsyncMock(side_effect=RuntimeError("elev err"))
        with patch("os.path.exists", return_value=True):
            resp = _post(client, "/api/geo/analytics/elevation-profile", {
                "dem_path": _FAKE_DEM, "points": [[0, 0]]
            })
        assert resp.status_code == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
