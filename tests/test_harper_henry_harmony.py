#!/usr/bin/env python3
"""
Integration tests for Harper Henry Harmony system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis.harper_henry_harmony_api import app
import json


def test_health_check():
    """Test API health check endpoint"""
    with app.test_client() as client:
        response = client.get('/healthz')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'harper-henry-harmony-api'
        print("✅ Health check test passed")


def test_metrics_endpoint():
    """Test metrics endpoint"""
    with app.test_client() as client:
        response = client.get('/api/v1/metrics')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'metrics' in data
        metrics = data['metrics']
        assert 'cultural_impact_score' in metrics
        assert 'economic_velocity' in metrics
        assert 'sustainability_score' in metrics
        assert 'harmony_score' in metrics
        print("✅ Metrics endpoint test passed")


def test_portfolio_status():
    """Test portfolio status endpoint"""
    with app.test_client() as client:
        response = client.get('/api/v1/portfolio/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'status' in data
        status = data['status']
        assert status['total_value'] == 100000
        assert len(status['assets']) >= 2
        print("✅ Portfolio status test passed")


def test_harmony_builders():
    """Test harmony builders endpoint"""
    with app.test_client() as client:
        response = client.get('/api/v1/harmony/builders')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'builders' in data
        builders = data['builders']
        assert len(builders) == 2
        assert builders[0]['builder_type'] == 'standard'
        assert builders[1]['builder_type'] == 'elite'
        print("✅ Harmony builders test passed")


def test_traditional_crafts():
    """Test traditional crafts endpoint"""
    with app.test_client() as client:
        response = client.get('/api/v1/traditional-crafts')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'crafts' in data
        crafts = data['crafts']
        assert len(crafts) == 3
        assert crafts[0]['craft_name'] == 'Japanese Pottery'
        assert crafts[1]['craft_name'] == 'Indian Textile Weaving'
        assert crafts[2]['craft_name'] == 'Mexican Woodcarving'
        print("✅ Traditional crafts test passed")


def test_optimization_engines():
    """Test optimization engines endpoint"""
    with app.test_client() as client:
        response = client.get('/api/v1/optimization/engines')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'engines' in data
        engines = data['engines']
        assert len(engines) == 3
        assert engines[0]['engine'] == 'harper_henry_harmony'
        assert engines[1]['engine'] == 'portfolio_optimization'
        assert engines[2]['engine'] == 'value_creation'
        print("✅ Optimization engines test passed")


def run_all_tests():
    """Run all integration tests"""
    print("\n🧪 Running Harper Henry Harmony Integration Tests...\n")
    
    try:
        test_health_check()
        test_metrics_endpoint()
        test_portfolio_status()
        test_harmony_builders()
        test_traditional_crafts()
        test_optimization_engines()
        
        print("\n✅ All integration tests passed!\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
