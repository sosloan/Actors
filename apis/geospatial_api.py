"""
Geospatial API for ACTORS

REST API for geospatial data processing using GDAL.
Enables location-based analytics for financial trading decisions.

Endpoints:
- POST /api/geo/raster/load - Load and analyze raster data
- POST /api/geo/raster/point-query - Query raster at specific point
- POST /api/geo/raster/ndvi - Compute NDVI for vegetation analysis
- POST /api/geo/vector/load - Load vector data
- POST /api/geo/vector/location-query - Query features by location
- POST /api/geo/vector/bbox-query - Query features by bounding box
- GET /api/geo/status - Get API status and cache info
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.geospatial_engine import GeospatialEngine, GDAL_AVAILABLE
from database.config import GeospatialConfig

app = Flask(__name__)
CORS(app)

# Initialize engine
config = GeospatialConfig()
engine = None

@app.before_request
def initialize_engine():
    """Initialize engine on first request"""
    global engine
    if engine is None:
        if not GDAL_AVAILABLE:
            return jsonify({
                "error": "GDAL dependencies not installed",
                "message": "Install with: pip install GDAL rasterio geopandas shapely"
            }), 500
        
        engine = GeospatialEngine(cache_dir=config.cache_dir)
        asyncio.run(engine.initialize())


# ==================== RASTER ENDPOINTS ====================

@app.route('/api/geo/raster/load', methods=['POST'])
def load_raster():
    """
    Load and analyze a raster dataset
    
    Request body:
    {
        "file_path": "/path/to/raster.tif",
        "cache_key": "optional_cache_key"
    }
    """
    try:
        data = request.json
        file_path = data.get('file_path')
        cache_key = data.get('cache_key')
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        result = asyncio.run(engine.load_raster(file_path, cache_key))
        
        # Convert numpy array to list for JSON serialization
        result_json = {
            "metadata": result["metadata"].to_dict(),
            "stats": result["stats"],
            "data_shape": result["data"].shape,
            "cached": cache_key is not None
        }
        
        return jsonify(result_json), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/geo/raster/point-query', methods=['POST'])
def query_raster_point():
    """
    Query raster value at a specific point
    
    Request body:
    {
        "file_path": "/path/to/raster.tif",
        "lon": -122.4194,
        "lat": 37.7749
    }
    """
    try:
        data = request.json
        file_path = data.get('file_path')
        lon = data.get('lon')
        lat = data.get('lat')
        
        if not all([file_path, lon is not None, lat is not None]):
            return jsonify({"error": "file_path, lon, and lat are required"}), 400
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        value = asyncio.run(engine.read_raster_at_point(file_path, lon, lat))
        
        return jsonify({
            "lon": lon,
            "lat": lat,
            "value": value
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/geo/raster/ndvi', methods=['POST'])
def compute_ndvi():
    """
    Compute NDVI (Normalized Difference Vegetation Index)
    
    Request body:
    {
        "red_band": "/path/to/red.tif",
        "nir_band": "/path/to/nir.tif"
    }
    
    Use case: Agricultural commodity trading based on crop health
    """
    try:
        data = request.json
        red_band = data.get('red_band')
        nir_band = data.get('nir_band')
        
        if not all([red_band, nir_band]):
            return jsonify({"error": "red_band and nir_band are required"}), 400
        
        if not os.path.exists(red_band):
            return jsonify({"error": f"Red band file not found: {red_band}"}), 404
        
        if not os.path.exists(nir_band):
            return jsonify({"error": f"NIR band file not found: {nir_band}"}), 404
        
        result = asyncio.run(engine.compute_ndvi(red_band, nir_band))
        
        result_json = {
            "metadata": result["metadata"].to_dict(),
            "stats": result["stats"],
            "ndvi_shape": result["ndvi"].shape,
            "interpretation": {
                "vegetation_cover_pct": result["stats"]["vegetation_cover_pct"],
                "health_rating": (
                    "Excellent" if result["stats"]["mean"] > 0.6 else
                    "Good" if result["stats"]["mean"] > 0.4 else
                    "Fair" if result["stats"]["mean"] > 0.2 else
                    "Poor"
                )
            }
        }
        
        return jsonify(result_json), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/geo/raster/statistics', methods=['POST'])
def raster_statistics():
    """
    Compute statistics for a raster dataset
    
    Request body:
    {
        "file_path": "/path/to/raster.tif"
    }
    """
    try:
        data = request.json
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        stats = asyncio.run(engine.compute_raster_statistics(file_path))
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== VECTOR ENDPOINTS ====================

@app.route('/api/geo/vector/load', methods=['POST'])
def load_vector():
    """
    Load and analyze a vector dataset
    
    Request body:
    {
        "file_path": "/path/to/vector.shp",
        "cache_key": "optional_cache_key"
    }
    """
    try:
        data = request.json
        file_path = data.get('file_path')
        cache_key = data.get('cache_key')
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        result = asyncio.run(engine.load_vector(file_path, cache_key))
        
        result_json = {
            "metadata": result["metadata"].to_dict(),
            "preview": result["preview"],
            "cached": cache_key is not None
        }
        
        return jsonify(result_json), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/geo/vector/location-query', methods=['POST'])
def query_vector_location():
    """
    Query vector features at or near a location
    
    Request body:
    {
        "file_path": "/path/to/vector.shp",
        "lon": -122.4194,
        "lat": 37.7749,
        "buffer_meters": 1000  // optional
    }
    
    Use case: Find POIs, facilities, or assets near a location
    """
    try:
        data = request.json
        file_path = data.get('file_path')
        lon = data.get('lon')
        lat = data.get('lat')
        buffer_meters = data.get('buffer_meters', 0)
        
        if not all([file_path, lon is not None, lat is not None]):
            return jsonify({"error": "file_path, lon, and lat are required"}), 400
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        results = asyncio.run(engine.query_vector_by_location(
            file_path, lon, lat, buffer_meters
        ))
        
        return jsonify({
            "query": {"lon": lon, "lat": lat, "buffer_meters": buffer_meters},
            "feature_count": len(results),
            "features": results
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/geo/vector/bbox-query', methods=['POST'])
def query_vector_bbox():
    """
    Query vector features within a bounding box
    
    Request body:
    {
        "file_path": "/path/to/vector.shp",
        "bbox": [minx, miny, maxx, maxy]  // e.g., [-122.5, 37.7, -122.3, 37.8]
    }
    
    Use case: Find all assets in a region for portfolio analysis
    """
    try:
        data = request.json
        file_path = data.get('file_path')
        bbox = data.get('bbox')
        
        if not all([file_path, bbox]):
            return jsonify({"error": "file_path and bbox are required"}), 400
        
        if len(bbox) != 4:
            return jsonify({"error": "bbox must be [minx, miny, maxx, maxy]"}), 400
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        
        results = asyncio.run(engine.query_vector_by_bbox(file_path, tuple(bbox)))
        
        return jsonify({
            "query": {"bbox": bbox},
            "feature_count": len(results),
            "features": results
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/geo/analytics/elevation-profile', methods=['POST'])
def elevation_profile():
    """
    Get elevation profile along a path
    
    Request body:
    {
        "dem_path": "/path/to/dem.tif",
        "points": [[lon1, lat1], [lon2, lat2], ...]
    }
    
    Use case: Route optimization, logistics planning
    """
    try:
        data = request.json
        dem_path = data.get('dem_path')
        points = data.get('points', [])
        
        if not dem_path:
            return jsonify({"error": "dem_path is required"}), 400
        
        if not points:
            return jsonify({"error": "points array is required"}), 400
        
        if not os.path.exists(dem_path):
            return jsonify({"error": f"DEM file not found: {dem_path}"}), 404
        
        profile = asyncio.run(engine.get_elevation_profile(dem_path, [tuple(p) for p in points]))
        
        # Compute additional metrics
        elevations = [p['elevation'] for p in profile if p['elevation'] is not None]
        
        metrics = {}
        if elevations:
            metrics = {
                "min_elevation": min(elevations),
                "max_elevation": max(elevations),
                "elevation_gain": sum(max(0, elevations[i] - elevations[i-1]) for i in range(1, len(elevations))),
                "elevation_loss": sum(max(0, elevations[i-1] - elevations[i]) for i in range(1, len(elevations)))
            }
        
        return jsonify({
            "profile": profile,
            "metrics": metrics
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== UTILITY ENDPOINTS ====================

@app.route('/api/geo/status', methods=['GET'])
def status():
    """Get API status and cache information"""
    try:
        cache_info = engine.get_cache_info() if engine else {}
        
        return jsonify({
            "status": "operational",
            "gdal_available": GDAL_AVAILABLE,
            "cache": cache_info,
            "config": {
                "cache_dir": config.cache_dir,
                "max_raster_size_mb": config.max_raster_size_mb,
                "enable_caching": config.enable_caching,
                "default_projection": config.default_projection
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/geo/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached datasets"""
    try:
        if engine:
            engine.clear_cache()
        
        return jsonify({
            "status": "success",
            "message": "Cache cleared"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/geo', methods=['GET'])
def api_info():
    """Get API information and available endpoints"""
    return jsonify({
        "name": "ACTORS Geospatial API",
        "description": "GDAL-powered geospatial data processing for financial trading",
        "version": "1.0.0",
        "gdal_available": GDAL_AVAILABLE,
        "endpoints": {
            "raster": {
                "POST /api/geo/raster/load": "Load and analyze raster data",
                "POST /api/geo/raster/point-query": "Query raster at specific point",
                "POST /api/geo/raster/ndvi": "Compute NDVI for vegetation analysis",
                "POST /api/geo/raster/statistics": "Compute raster statistics"
            },
            "vector": {
                "POST /api/geo/vector/load": "Load and analyze vector data",
                "POST /api/geo/vector/location-query": "Query features by location",
                "POST /api/geo/vector/bbox-query": "Query features by bounding box"
            },
            "analytics": {
                "POST /api/geo/analytics/elevation-profile": "Get elevation profile along path"
            },
            "utility": {
                "GET /api/geo/status": "Get API status",
                "POST /api/geo/cache/clear": "Clear cache",
                "GET /api/geo": "API information"
            }
        },
        "use_cases": [
            "Agricultural commodity trading (crop monitoring via NDVI)",
            "Real estate analysis (location intelligence)",
            "Supply chain optimization (route analysis)",
            "Climate risk assessment (environmental data)",
            "Alternative data signals (satellite observations)"
        ]
    }), 200


if __name__ == '__main__':
    print("🌍 Starting ACTORS Geospatial API...")
    print(f"   GDAL Available: {GDAL_AVAILABLE}")
    print(f"   Cache Directory: {config.cache_dir}")
    print(f"   Default Projection: {config.default_projection}")
    print("\n📡 API Endpoints:")
    print("   GET  /api/geo - API information")
    print("   GET  /api/geo/status - System status")
    print("   POST /api/geo/raster/load - Load raster data")
    print("   POST /api/geo/raster/point-query - Query raster at point")
    print("   POST /api/geo/raster/ndvi - Compute NDVI")
    print("   POST /api/geo/vector/load - Load vector data")
    print("   POST /api/geo/vector/location-query - Query by location")
    print("   POST /api/geo/vector/bbox-query - Query by bounding box")
    print("\n🚀 Starting server on http://localhost:5004")
    
    app.run(host='0.0.0.0', port=5004, debug=True)
