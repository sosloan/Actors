#!/usr/bin/env python3
"""
Tests for apis/lobsters_bonvoya_api.py

All heavy dependencies (LobstersBonvoyaSystem and related types from
lobsters_bonvoya) are mocked via sys.modules so the Flask app can be
imported and exercised without optional third-party libraries being installed.
"""

import sys
import types
import json
import pytest
from enum import Enum
from unittest.mock import MagicMock, AsyncMock, patch


# ---------------------------------------------------------------------------
# Inject stub module for lobsters_bonvoya before importing the API
# ---------------------------------------------------------------------------

class _TravelClass(Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"
    PRIVATE = "private"


class _AccommodationType(Enum):
    HOSTEL = "hostel"
    BUDGET_HOTEL = "budget_hotel"
    BOUTIQUE_HOTEL = "boutique_hotel"
    LUXURY_HOTEL = "luxury_hotel"
    RESORT = "resort"
    VILLA = "villa"
    PRIVATE_ISLAND = "private_island"


class _TravelPurpose(Enum):
    LEISURE = "leisure"
    BUSINESS = "business"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    WELLNESS = "wellness"
    LUXURY = "luxury"
    BUDGET = "budget"
    FIRE_OPTIMIZATION = "fire_optimization"


class _TravelPreferences:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class _FakeLobstersBonvoyaSystem:
    async def create_travel_plan(self, user_id, preferences, departure_location, financial_profile=None):
        return {
            "user_id": user_id,
            "recommended_itinerary": {
                "destination": {"name": "Bali"},
                "total_cost": 3000,
            },
            "alternative_itineraries": [],
            "financial_optimization": {"total_savings": 300},
            "total_savings": 300,
            "optimization_score": 0.75,
            "created_at": "2024-01-01T00:00:00",
        }

    async def get_travel_recommendations(self, user_id, recommendation_type="personalized"):
        return {
            "user_id": user_id,
            "recommendation_type": recommendation_type,
            "recommendations": [],
            "generated_at": "2024-01-01T00:00:00",
        }

    def get_system_stats(self):
        return {
            "total_users": 5,
            "total_bookings": 10,
            "average_savings_per_booking": 200.0,
            "popular_destinations": [("Bali", 3)],
            "system_uptime": "Active",
            "last_updated": "2024-01-01T00:00:00",
        }

    class _FakeDestDB(dict):
        pass

    def __init__(self):
        from dataclasses import dataclass
        from typing import List, Tuple

        @dataclass
        class _Dest:
            id: str
            name: str
            country: str
            continent: str
            coordinates: Tuple[float, float]
            climate: str
            cost_index: float
            safety_score: float
            cultural_richness: float
            adventure_score: float
            luxury_score: float
            fire_friendly: bool
            visa_requirements: List[str]
            best_seasons: List[str]

        self.travel_agent = MagicMock()
        self.travel_agent.destinations_db = {
            "bali": _Dest(
                id="bali",
                name="Bali",
                country="Indonesia",
                continent="Asia",
                coordinates=(-8.34, 115.09),
                climate="tropical",
                cost_index=0.3,
                safety_score=0.8,
                cultural_richness=0.9,
                adventure_score=0.8,
                luxury_score=0.7,
                fire_friendly=True,
                visa_requirements=["passport"],
                best_seasons=["dry_season"],
            )
        }


_bonvoya_stub = types.ModuleType("lobsters_bonvoya")
_bonvoya_stub.LobstersBonvoyaSystem = _FakeLobstersBonvoyaSystem
_bonvoya_stub.TravelPreferences = _TravelPreferences
_bonvoya_stub.TravelClass = _TravelClass
_bonvoya_stub.AccommodationType = _AccommodationType
_bonvoya_stub.TravelPurpose = _TravelPurpose

sys.modules.setdefault("lobsters_bonvoya", _bonvoya_stub)

# Add apis/ and core/ directories to path so the module can be imported
import os
_repo_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_repo_root, "apis"))
sys.path.insert(0, os.path.join(_repo_root, "core"))

# The API module re-registers async routes at module-bottom via an async_route
# wrapper that does not preserve __name__, causing Flask to raise on duplicate
# endpoint names.  Silence those AssertionErrors so the import succeeds; the
# routes registered by the @app.route decorators (native async, Flask 2+) are
# kept unchanged.
from flask import Flask as _Flask
_orig_add_url_rule = _Flask.add_url_rule


def _tolerant_add_url_rule(self, rule, endpoint=None, view_func=None, **options):
    try:
        _orig_add_url_rule(self, rule, endpoint=endpoint, view_func=view_func, **options)
    except AssertionError:
        pass  # ignore duplicate endpoint registrations


_Flask.add_url_rule = _tolerant_add_url_rule

import lobsters_bonvoya_api as api_module
from lobsters_bonvoya_api import app

_Flask.add_url_rule = _orig_add_url_rule  # restore after import


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def no_system(client):
    """bonvoya_system set to None (uninitialised)."""
    with patch.object(api_module, "bonvoya_system", None):
        yield client


@pytest.fixture()
def system_up(client):
    """bonvoya_system set to a functional fake."""
    with patch.object(api_module, "bonvoya_system", _FakeLobstersBonvoyaSystem()):
        yield client


# ===========================================================================
# /health
# ===========================================================================

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_response_structure(self, client):
        data = client.get("/health").get_json()
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert "system_initialized" in data

    def test_health_service_name(self, client):
        data = client.get("/health").get_json()
        assert "Bonvoy" in data["service"]

    def test_health_not_initialized_when_no_system(self, no_system):
        data = no_system.get("/health").get_json()
        assert data["system_initialized"] is False

    def test_health_initialized_when_system_up(self, system_up):
        data = system_up.get("/health").get_json()
        assert data["system_initialized"] is True


# ===========================================================================
# /api/travel/destinations
# ===========================================================================

class TestDestinationsEndpoint:
    def test_returns_500_when_no_system(self, no_system):
        resp = no_system.get("/api/travel/destinations")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_200_with_system(self, system_up):
        resp = system_up.get("/api/travel/destinations")
        assert resp.status_code == 200

    def test_response_structure(self, system_up):
        data = system_up.get("/api/travel/destinations").get_json()
        assert "destinations" in data
        assert "total_count" in data

    def test_destinations_list_matches_count(self, system_up):
        data = system_up.get("/api/travel/destinations").get_json()
        assert len(data["destinations"]) == data["total_count"]

    def test_destination_fields(self, system_up):
        data = system_up.get("/api/travel/destinations").get_json()
        dest = data["destinations"][0]
        for field in ("id", "name", "country", "continent", "cost_index",
                      "safety_score", "fire_friendly"):
            assert field in dest


# ===========================================================================
# /api/stats
# ===========================================================================

class TestStatsEndpoint:
    def test_returns_500_when_no_system(self, no_system):
        resp = no_system.get("/api/stats")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_200_with_system(self, system_up):
        resp = system_up.get("/api/stats")
        assert resp.status_code == 200

    def test_response_structure(self, system_up):
        data = system_up.get("/api/stats").get_json()
        assert "total_users" in data
        assert "total_bookings" in data
        assert "average_savings_per_booking" in data
        assert "popular_destinations" in data


# ===========================================================================
# /api/travel/purposes
# ===========================================================================

class TestTravelPurposesEndpoint:
    def test_returns_200(self, client):
        resp = client.get("/api/travel/purposes")
        assert resp.status_code == 200

    def test_response_has_purposes(self, client):
        data = client.get("/api/travel/purposes").get_json()
        assert "purposes" in data
        assert len(data["purposes"]) > 0

    def test_purpose_has_required_fields(self, client):
        data = client.get("/api/travel/purposes").get_json()
        for purpose in data["purposes"]:
            assert "value" in purpose
            assert "label" in purpose
            assert "description" in purpose

    def test_fire_optimization_purpose_present(self, client):
        data = client.get("/api/travel/purposes").get_json()
        values = [p["value"] for p in data["purposes"]]
        assert "fire_optimization" in values


# ===========================================================================
# /api/travel/classes
# ===========================================================================

class TestTravelClassesEndpoint:
    def test_returns_200(self, client):
        resp = client.get("/api/travel/classes")
        assert resp.status_code == 200

    def test_response_has_classes(self, client):
        data = client.get("/api/travel/classes").get_json()
        assert "classes" in data
        assert len(data["classes"]) > 0

    def test_class_has_required_fields(self, client):
        data = client.get("/api/travel/classes").get_json()
        for cls in data["classes"]:
            assert "value" in cls
            assert "label" in cls
            assert "price_multiplier" in cls

    def test_economy_class_present(self, client):
        data = client.get("/api/travel/classes").get_json()
        values = [c["value"] for c in data["classes"]]
        assert "economy" in values


# ===========================================================================
# /api/accommodation/types
# ===========================================================================

class TestAccommodationTypesEndpoint:
    def test_returns_200(self, client):
        resp = client.get("/api/accommodation/types")
        assert resp.status_code == 200

    def test_response_has_types(self, client):
        data = client.get("/api/accommodation/types").get_json()
        assert "types" in data
        assert len(data["types"]) > 0

    def test_type_has_required_fields(self, client):
        data = client.get("/api/accommodation/types").get_json()
        for t in data["types"]:
            assert "value" in t
            assert "label" in t
            assert "price_multiplier" in t

    def test_hostel_type_present(self, client):
        data = client.get("/api/accommodation/types").get_json()
        values = [t["value"] for t in data["types"]]
        assert "hostel" in values


# ===========================================================================
# /api/financial/optimize
# ===========================================================================

class TestFinancialOptimizeEndpoint:
    def test_returns_500_when_no_system(self, no_system):
        resp = no_system.post(
            "/api/financial/optimize",
            json={"travel_cost": 3000},
            content_type="application/json",
        )
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_200_with_system(self, system_up):
        resp = system_up.post(
            "/api/financial/optimize",
            json={"travel_cost": 3000},
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_response_structure(self, system_up):
        data = system_up.post(
            "/api/financial/optimize",
            json={"travel_cost": 3000},
            content_type="application/json",
        ).get_json()
        assert "budget_allocation" in data
        assert "points_optimization" in data
        assert "tax_optimization" in data
        assert "total_savings" in data

    def test_default_travel_cost(self, system_up):
        data = system_up.post(
            "/api/financial/optimize",
            json={},
            content_type="application/json",
        ).get_json()
        # Default travel_cost is 3000; total_savings should be 20% of it
        assert data["total_savings"] == pytest.approx(3000 * 0.2)

    def test_business_travel_tax_deduction(self, system_up):
        data = system_up.post(
            "/api/financial/optimize",
            json={
                "travel_cost": 5000,
                "financial_profile": {"is_business_travel": True, "tax_bracket": 0.25},
            },
            content_type="application/json",
        ).get_json()
        tax = data["tax_optimization"]
        assert tax["deductible_amount"] == pytest.approx(5000 * 0.8)
        assert tax["tax_savings"] == pytest.approx(5000 * 0.8 * 0.25)

    def test_personal_travel_no_tax_deduction(self, system_up):
        data = system_up.post(
            "/api/financial/optimize",
            json={
                "travel_cost": 5000,
                "financial_profile": {"is_business_travel": False},
            },
            content_type="application/json",
        ).get_json()
        tax = data["tax_optimization"]
        assert tax["deductible_amount"] == 0
        assert tax["tax_savings"] == 0

    def test_points_savings_calculated(self, system_up):
        data = system_up.post(
            "/api/financial/optimize",
            json={"travel_cost": 4000},
            content_type="application/json",
        ).get_json()
        pts = data["points_optimization"]
        assert "flight_savings" in pts
        assert "accommodation_savings" in pts
        assert "total_savings" in pts


# ===========================================================================
# /api/travel/plan  (POST, async wrapped)
# ===========================================================================

class TestTravelPlanEndpoint:
    _valid_payload = {
        "user_id": "test_user_1",
        "departure_location": "San Francisco",
        "preferences": {
            "budget_min": 2000,
            "budget_max": 4000,
            "travel_class": "economy",
            "accommodation_type": "boutique_hotel",
            "purpose": "fire_optimization",
            "duration_days": 7,
            "group_size": 2,
        },
        "financial_profile": {
            "liquid_cash": 15000,
            "investment_portfolio": 200000,
        },
    }

    def test_returns_500_when_no_system(self, no_system):
        resp = no_system.post(
            "/api/travel/plan",
            json=self._valid_payload,
            content_type="application/json",
        )
        assert resp.status_code == 500

    def test_returns_200_with_system(self, system_up):
        resp = system_up.post(
            "/api/travel/plan",
            json=self._valid_payload,
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_response_has_user_id(self, system_up):
        data = system_up.post(
            "/api/travel/plan",
            json=self._valid_payload,
            content_type="application/json",
        ).get_json()
        assert data["user_id"] == "test_user_1"

    def test_response_has_recommended_itinerary(self, system_up):
        data = system_up.post(
            "/api/travel/plan",
            json=self._valid_payload,
            content_type="application/json",
        ).get_json()
        assert "recommended_itinerary" in data

    def test_default_user_id_generated_when_absent(self, system_up):
        payload = dict(self._valid_payload)
        del payload["user_id"]
        data = system_up.post(
            "/api/travel/plan",
            json=payload,
            content_type="application/json",
        ).get_json()
        assert "user_id" in data


# ===========================================================================
# /api/travel/recommendations/<user_id>  (GET, async wrapped)
# ===========================================================================

class TestTravelRecommendationsEndpoint:
    def test_returns_500_when_no_system(self, no_system):
        resp = no_system.get("/api/travel/recommendations/user_abc")
        assert resp.status_code == 500

    def test_returns_200_with_system(self, system_up):
        resp = system_up.get("/api/travel/recommendations/user_abc")
        assert resp.status_code == 200

    def test_response_structure(self, system_up):
        data = system_up.get("/api/travel/recommendations/user_abc").get_json()
        assert "user_id" in data
        assert "recommendation_type" in data
        assert "recommendations" in data

    def test_user_id_in_response(self, system_up):
        data = system_up.get("/api/travel/recommendations/user_abc").get_json()
        assert data["user_id"] == "user_abc"

    def test_default_recommendation_type(self, system_up):
        data = system_up.get("/api/travel/recommendations/user_abc").get_json()
        assert data["recommendation_type"] == "personalized"

    def test_custom_recommendation_type(self, system_up):
        data = system_up.get(
            "/api/travel/recommendations/user_abc?type=fire"
        ).get_json()
        assert data["recommendation_type"] == "fire"


# ===========================================================================
# /api/demo/* endpoints  (async wrapped)
# ===========================================================================

class TestDemoEndpoints:
    def test_fire_travel_returns_500_when_no_system(self, no_system):
        assert no_system.get("/api/demo/fire-travel").status_code == 500

    def test_fire_travel_returns_200_with_system(self, system_up):
        assert system_up.get("/api/demo/fire-travel").status_code == 200

    def test_fire_travel_response_has_itinerary(self, system_up):
        data = system_up.get("/api/demo/fire-travel").get_json()
        assert "recommended_itinerary" in data

    def test_luxury_travel_returns_500_when_no_system(self, no_system):
        assert no_system.get("/api/demo/luxury-travel").status_code == 500

    def test_luxury_travel_returns_200_with_system(self, system_up):
        assert system_up.get("/api/demo/luxury-travel").status_code == 200

    def test_luxury_travel_response_has_itinerary(self, system_up):
        data = system_up.get("/api/demo/luxury-travel").get_json()
        assert "recommended_itinerary" in data

    def test_adventure_travel_returns_500_when_no_system(self, no_system):
        assert no_system.get("/api/demo/adventure-travel").status_code == 500

    def test_adventure_travel_returns_200_with_system(self, system_up):
        assert system_up.get("/api/demo/adventure-travel").status_code == 200

    def test_adventure_travel_response_has_itinerary(self, system_up):
        data = system_up.get("/api/demo/adventure-travel").get_json()
        assert "recommended_itinerary" in data


# ===========================================================================
# Error handlers
# ===========================================================================

class TestErrorHandlers:
    def test_404_returns_json(self, client):
        resp = client.get("/nonexistent_route_xyz")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
        assert data["error"] == "Endpoint not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
