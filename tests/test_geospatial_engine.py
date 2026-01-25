"""
Tests for Geospatial Engine

Tests the GDAL-powered geospatial data processing capabilities.
"""

import pytest
import numpy as np
import asyncio
import tempfile
import os
from pathlib import Path

# Import the module
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.geospatial_engine import GeospatialEngine, GDAL_AVAILABLE, RasterMetadata, VectorMetadata
from database.config import GeospatialConfig


# Skip all tests if GDAL is not available
pytestmark = pytest.mark.skipif(not GDAL_AVAILABLE, reason="GDAL not available")


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
async def engine(temp_cache_dir):
    """Create geospatial engine instance"""
    eng = GeospatialEngine(cache_dir=temp_cache_dir)
    await eng.initialize()
    return eng


@pytest.fixture
def synthetic_raster_file():
    """Create a synthetic raster file for testing"""
    if not GDAL_AVAILABLE:
        return None
    
    import rasterio
    from rasterio.transform import from_bounds
    
    # Create synthetic data
    width, height = 50, 50
    data = np.random.rand(height, width).astype(np.float32)
    
    # Create temporary file
    tmpfile = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
    tmpfile.close()
    
    # Write GeoTIFF
    transform = from_bounds(-180, -90, 180, 90, width, height)
    
    with rasterio.open(
        tmpfile.name,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=rasterio.float32,
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        dst.write(data, 1)
    
    yield tmpfile.name
    
    # Cleanup
    os.unlink(tmpfile.name)


@pytest.fixture
def synthetic_vector_file():
    """Create a synthetic vector file for testing"""
    if not GDAL_AVAILABLE:
        return None
    
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Create synthetic point data
    points = [
        Point(-122.4194, 37.7749),  # San Francisco
        Point(-118.2437, 34.0522),  # Los Angeles
        Point(-73.9352, 40.7306),   # New York
    ]
    
    gdf = gpd.GeoDataFrame({
        'name': ['SF', 'LA', 'NY'],
        'population': [874961, 3979576, 8336817]
    }, geometry=points, crs='EPSG:4326')
    
    tmpfile = tempfile.NamedTemporaryFile(suffix='.geojson', delete=False)
    tmpfile.close()
    
    gdf.to_file(tmpfile.name, driver='GeoJSON')
    
    yield tmpfile.name
    
    # Cleanup
    os.unlink(tmpfile.name)


class TestGeospatialEngine:
    """Test GeospatialEngine class"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, temp_cache_dir):
        """Test engine initialization"""
        engine = GeospatialEngine(cache_dir=temp_cache_dir)
        await engine.initialize()
        
        assert engine.cache_dir.exists()
        assert engine._raster_cache == {}
        assert engine._vector_cache == {}
    
    @pytest.mark.asyncio
    async def test_load_raster(self, engine, synthetic_raster_file):
        """Test loading raster data"""
        result = await engine.load_raster(synthetic_raster_file)
        
        assert 'data' in result
        assert 'metadata' in result
        assert 'stats' in result
        
        # Check metadata
        metadata = result['metadata']
        assert isinstance(metadata, RasterMetadata)
        assert metadata.width == 50
        assert metadata.height == 50
        assert metadata.bands == 1
        
        # Check stats
        stats = result['stats']
        assert 'min' in stats
        assert 'max' in stats
        assert 'mean' in stats
        assert 'std' in stats
    
    @pytest.mark.asyncio
    async def test_raster_caching(self, engine, synthetic_raster_file):
        """Test raster caching"""
        # Load with cache key
        result1 = await engine.load_raster(synthetic_raster_file, cache_key='test_raster')
        
        # Load again with same cache key (should use cache)
        result2 = await engine.load_raster(synthetic_raster_file, cache_key='test_raster')
        
        # Should be the same object
        assert result1 is result2
        
        # Check cache info
        cache_info = engine.get_cache_info()
        assert 'test_raster' in cache_info['raster_cache']
    
    @pytest.mark.asyncio
    async def test_read_raster_at_point(self, engine, synthetic_raster_file):
        """Test reading raster value at a point"""
        # Query at center of raster
        value = await engine.read_raster_at_point(synthetic_raster_file, 0, 0)
        
        assert value is not None
        assert isinstance(value, float)
        assert 0 <= value <= 1  # Our synthetic data is in [0, 1]
    
    @pytest.mark.asyncio
    async def test_compute_ndvi(self, engine):
        """Test NDVI computation"""
        import rasterio
        from rasterio.transform import from_bounds
        
        # Create synthetic red and NIR bands
        width, height = 50, 50
        transform = from_bounds(-180, -90, 180, 90, width, height)
        
        # Red band (low values)
        red_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
        red_file.close()
        red_data = np.random.rand(height, width).astype(np.float32) * 0.3
        
        with rasterio.open(
            red_file.name, 'w', driver='GTiff',
            height=height, width=width, count=1,
            dtype=rasterio.float32, crs='EPSG:4326', transform=transform
        ) as dst:
            dst.write(red_data, 1)
        
        # NIR band (high values)
        nir_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
        nir_file.close()
        nir_data = np.random.rand(height, width).astype(np.float32) * 0.3 + 0.6
        
        with rasterio.open(
            nir_file.name, 'w', driver='GTiff',
            height=height, width=width, count=1,
            dtype=rasterio.float32, crs='EPSG:4326', transform=transform
        ) as dst:
            dst.write(nir_data, 1)
        
        try:
            # Compute NDVI
            result = await engine.compute_ndvi(red_file.name, nir_file.name)
            
            assert 'ndvi' in result
            assert 'metadata' in result
            assert 'stats' in result
            
            # NDVI should be positive (NIR > Red)
            assert result['stats']['mean'] > 0
            
            # NDVI should be in valid range [-1, 1]
            assert -1 <= result['stats']['min'] <= 1
            assert -1 <= result['stats']['max'] <= 1
            
        finally:
            # Cleanup
            os.unlink(red_file.name)
            os.unlink(nir_file.name)
    
    @pytest.mark.asyncio
    async def test_load_vector(self, engine, synthetic_vector_file):
        """Test loading vector data"""
        result = await engine.load_vector(synthetic_vector_file)
        
        assert 'gdf' in result
        assert 'metadata' in result
        assert 'preview' in result
        
        # Check metadata
        metadata = result['metadata']
        assert isinstance(metadata, VectorMetadata)
        assert metadata.feature_count == 3
        assert metadata.geometry_type == 'Point'
        
        # Check preview
        assert len(result['preview']) <= 5
    
    @pytest.mark.asyncio
    async def test_vector_caching(self, engine, synthetic_vector_file):
        """Test vector caching"""
        # Load with cache key
        result1 = await engine.load_vector(synthetic_vector_file, cache_key='test_vector')
        
        # Load again with same cache key
        result2 = await engine.load_vector(synthetic_vector_file, cache_key='test_vector')
        
        # GDF should be the same object from cache
        assert result1['gdf'] is result2['gdf']
        
        # Check cache info
        cache_info = engine.get_cache_info()
        assert 'test_vector' in cache_info['vector_cache']
    
    @pytest.mark.asyncio
    async def test_query_vector_by_location(self, engine, synthetic_vector_file):
        """Test querying vector features by location"""
        # Query near San Francisco
        results = await engine.query_vector_by_location(
            synthetic_vector_file,
            lon=-122.4194,
            lat=37.7749,
            buffer_meters=1000
        )
        
        assert len(results) >= 1
        assert any(r['name'] == 'SF' for r in results)
    
    @pytest.mark.asyncio
    async def test_query_vector_by_bbox(self, engine, synthetic_vector_file):
        """Test querying vector features by bounding box"""
        # Bounding box around western US (should include SF and LA)
        bbox = (-125, 32, -115, 40)
        
        results = await engine.query_vector_by_bbox(synthetic_vector_file, bbox)
        
        assert len(results) >= 2
        names = [r['name'] for r in results]
        assert 'SF' in names
        assert 'LA' in names
    
    @pytest.mark.asyncio
    async def test_compute_raster_statistics(self, engine, synthetic_raster_file):
        """Test computing raster statistics"""
        stats = await engine.compute_raster_statistics(synthetic_raster_file)
        
        assert 'min' in stats
        assert 'max' in stats
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'percentile_25' in stats
        assert 'percentile_75' in stats
        
        # Basic sanity checks
        assert stats['min'] <= stats['mean'] <= stats['max']
        assert stats['percentile_25'] <= stats['median'] <= stats['percentile_75']
    
    @pytest.mark.asyncio
    async def test_get_elevation_profile(self, engine, synthetic_raster_file):
        """Test getting elevation profile"""
        points = [
            (0, 0),
            (10, 10),
            (20, 20)
        ]
        
        profile = await engine.get_elevation_profile(synthetic_raster_file, points)
        
        assert len(profile) == 3
        for point in profile:
            assert 'lon' in point
            assert 'lat' in point
            assert 'elevation' in point
    
    def test_clear_cache(self, engine, synthetic_raster_file):
        """Test clearing cache"""
        # Load something to populate cache
        asyncio.run(engine.load_raster(synthetic_raster_file, cache_key='test'))
        
        # Verify cache is populated
        cache_info = engine.get_cache_info()
        assert len(cache_info['raster_cache']) > 0
        
        # Clear cache
        engine.clear_cache()
        
        # Verify cache is empty
        cache_info = engine.get_cache_info()
        assert len(cache_info['raster_cache']) == 0
        assert len(cache_info['vector_cache']) == 0


class TestGeospatialConfig:
    """Test GeospatialConfig class"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = GeospatialConfig()
        
        assert config.cache_dir == "/tmp/geospatial_cache"
        assert config.max_raster_size_mb == 500
        assert config.enable_caching is True
        assert config.default_projection == "EPSG:4326"
        assert config.enable_compression is True
        assert config.tile_size == 256


class TestRasterMetadata:
    """Test RasterMetadata dataclass"""
    
    def test_to_dict(self):
        """Test metadata serialization to dict"""
        metadata = RasterMetadata(
            width=100,
            height=100,
            bands=1,
            projection="EPSG:4326",
            geotransform=(0, 1, 0, 0, 0, 1),
            bounds=(0, 0, 100, 100),
            nodata_value=-9999
        )
        
        result = metadata.to_dict()
        
        assert result['width'] == 100
        assert result['height'] == 100
        assert result['bands'] == 1
        assert result['projection'] == "EPSG:4326"
        assert result['geotransform'] == [0, 1, 0, 0, 0, 1]
        assert result['bounds'] == [0, 0, 100, 100]
        assert result['nodata_value'] == -9999


class TestVectorMetadata:
    """Test VectorMetadata dataclass"""
    
    def test_to_dict(self):
        """Test metadata serialization to dict"""
        metadata = VectorMetadata(
            feature_count=10,
            geometry_type="Point",
            projection="EPSG:4326",
            bounds=(0, 0, 100, 100),
            fields=['name', 'value']
        )
        
        result = metadata.to_dict()
        
        assert result['feature_count'] == 10
        assert result['geometry_type'] == "Point"
        assert result['projection'] == "EPSG:4326"
        assert result['bounds'] == [0, 0, 100, 100]
        assert result['fields'] == ['name', 'value']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
