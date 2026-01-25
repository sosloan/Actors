"""
Geospatial Engine for ACTORS

Provides GDAL-powered geospatial data processing capabilities for:
- Raster data analysis (satellite imagery, terrain data, etc.)
- Vector data processing (boundaries, locations, routes)
- Geospatial analytics for trading decisions
- Alternative data integration (satellite observations, geographic trends)

Integrates with:
- L0: Hot state for frequently accessed geo features
- L2: Analytics store for spatial queries and historical data
"""

import os
import asyncio
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json

try:
    from osgeo import gdal, ogr, osr
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    import geopandas as gpd
    from shapely.geometry import Point, Polygon, box
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False
    print("Warning: GDAL/geospatial dependencies not available. Install with: pip install GDAL rasterio geopandas")


@dataclass
class RasterMetadata:
    """Metadata for a raster dataset"""
    width: int
    height: int
    bands: int
    projection: str
    geotransform: Tuple[float, ...]
    bounds: Tuple[float, float, float, float]  # (minx, miny, maxx, maxy)
    nodata_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "bands": self.bands,
            "projection": self.projection,
            "geotransform": list(self.geotransform),
            "bounds": list(self.bounds),
            "nodata_value": self.nodata_value
        }


@dataclass
class VectorMetadata:
    """Metadata for a vector dataset"""
    feature_count: int
    geometry_type: str
    projection: str
    bounds: Tuple[float, float, float, float]
    fields: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_count": self.feature_count,
            "geometry_type": self.geometry_type,
            "projection": self.projection,
            "bounds": list(self.bounds),
            "fields": self.fields
        }


class GeospatialEngine:
    """
    Geospatial data processing engine powered by GDAL
    
    Capabilities:
    - Load and process raster data (GeoTIFF, COG, etc.)
    - Load and query vector data (Shapefile, GeoJSON, etc.)
    - Perform geospatial analytics (NDVI, terrain analysis, etc.)
    - Integrate with financial models (location-based trading signals)
    """
    
    def __init__(self, cache_dir: str = "/tmp/geospatial_cache"):
        """Initialize geospatial engine"""
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL dependencies not available. Install with: pip install GDAL rasterio geopandas")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Enable GDAL exceptions for better error handling
        gdal.UseExceptions()
        
        # Cache for loaded datasets
        self._raster_cache: Dict[str, Any] = {}
        self._vector_cache: Dict[str, gpd.GeoDataFrame] = {}
        
        print(f"🌍 GeospatialEngine initialized with cache at {self.cache_dir}")
        print(f"   GDAL version: {gdal.__version__}")
    
    async def initialize(self):
        """Async initialization"""
        print("🌍 GeospatialEngine ready")
    
    # ==================== RASTER OPERATIONS ====================
    
    async def load_raster(self, file_path: str, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a raster dataset (GeoTIFF, COG, etc.)
        
        Args:
            file_path: Path to raster file
            cache_key: Optional cache key for faster reloading
            
        Returns:
            Dictionary with raster data and metadata
        """
        if cache_key and cache_key in self._raster_cache:
            print(f"📦 Loading raster from cache: {cache_key}")
            return self._raster_cache[cache_key]
        
        print(f"📥 Loading raster: {file_path}")
        
        with rasterio.open(file_path) as src:
            # Read metadata
            metadata = RasterMetadata(
                width=src.width,
                height=src.height,
                bands=src.count,
                projection=src.crs.to_string() if src.crs else "Unknown",
                geotransform=src.transform.to_gdal(),
                bounds=src.bounds,
                nodata_value=src.nodata
            )
            
            # Read data (convert to numpy array)
            # For efficiency, only load first band by default
            data = src.read(1)  # Shape: (height, width)
            
            result = {
                "data": data,
                "metadata": metadata,
                "stats": {
                    "min": float(np.nanmin(data)),
                    "max": float(np.nanmax(data)),
                    "mean": float(np.nanmean(data)),
                    "std": float(np.nanstd(data))
                }
            }
            
            if cache_key:
                self._raster_cache[cache_key] = result
            
            print(f"✅ Raster loaded: {metadata.width}x{metadata.height}, {metadata.bands} bands")
            return result
    
    async def read_raster_at_point(self, file_path: str, lon: float, lat: float) -> Optional[float]:
        """
        Read raster value at a specific point (lon, lat)
        
        Args:
            file_path: Path to raster file
            lon: Longitude
            lat: Latitude
            
        Returns:
            Raster value at the point, or None if outside bounds
        """
        with rasterio.open(file_path) as src:
            # Convert lon/lat to row/col
            row, col = src.index(lon, lat)
            
            # Check if within bounds
            if 0 <= row < src.height and 0 <= col < src.width:
                data = src.read(1)
                return float(data[row, col])
            else:
                return None
    
    async def compute_ndvi(self, red_band_path: str, nir_band_path: str) -> Dict[str, Any]:
        """
        Compute NDVI (Normalized Difference Vegetation Index)
        NDVI = (NIR - Red) / (NIR + Red)
        
        Useful for:
        - Agricultural commodity trading (crop health monitoring)
        - Real estate valuation (green space analysis)
        - Climate risk assessment
        
        Args:
            red_band_path: Path to red band raster
            nir_band_path: Path to near-infrared band raster
            
        Returns:
            NDVI raster data and statistics
        """
        print("🌿 Computing NDVI...")
        
        # Load bands
        red_data = await self.load_raster(red_band_path)
        nir_data = await self.load_raster(nir_band_path)
        
        red = red_data["data"].astype(float)
        nir = nir_data["data"].astype(float)
        
        # Compute NDVI
        # Handle division by zero
        denominator = nir + red
        ndvi = np.where(denominator != 0, (nir - red) / denominator, 0)
        
        result = {
            "ndvi": ndvi,
            "metadata": red_data["metadata"],  # Assume same metadata
            "stats": {
                "min": float(np.nanmin(ndvi)),
                "max": float(np.nanmax(ndvi)),
                "mean": float(np.nanmean(ndvi)),
                "vegetation_cover_pct": float(np.sum(ndvi > 0.3) / ndvi.size * 100)
            }
        }
        
        print(f"✅ NDVI computed: vegetation cover ~{result['stats']['vegetation_cover_pct']:.1f}%")
        return result
    
    # ==================== VECTOR OPERATIONS ====================
    
    async def load_vector(self, file_path: str, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a vector dataset (Shapefile, GeoJSON, etc.)
        
        Args:
            file_path: Path to vector file
            cache_key: Optional cache key for faster reloading
            
        Returns:
            Dictionary with vector data and metadata
        """
        if cache_key and cache_key in self._vector_cache:
            print(f"📦 Loading vector from cache: {cache_key}")
            gdf = self._vector_cache[cache_key]
        else:
            print(f"📥 Loading vector: {file_path}")
            gdf = gpd.read_file(file_path)
            
            if cache_key:
                self._vector_cache[cache_key] = gdf
        
        # Extract metadata
        metadata = VectorMetadata(
            feature_count=len(gdf),
            geometry_type=gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Unknown",
            projection=gdf.crs.to_string() if gdf.crs else "Unknown",
            bounds=tuple(gdf.total_bounds),
            fields=list(gdf.columns)
        )
        
        result = {
            "gdf": gdf,
            "metadata": metadata,
            "preview": gdf.head(5).to_dict('records')
        }
        
        print(f"✅ Vector loaded: {metadata.feature_count} features, type: {metadata.geometry_type}")
        return result
    
    async def query_vector_by_location(
        self, 
        file_path: str, 
        lon: float, 
        lat: float, 
        buffer_meters: float = 0
    ) -> List[Dict[str, Any]]:
        """
        Query vector features at or near a location
        
        Args:
            file_path: Path to vector file
            lon: Longitude
            lat: Latitude
            buffer_meters: Buffer distance in meters
            
        Returns:
            List of features intersecting the location/buffer
        """
        gdf = gpd.read_file(file_path)
        
        # Create point geometry
        point = Point(lon, lat)
        point_gdf = gpd.GeoDataFrame([{'geometry': point}], crs='EPSG:4326')
        
        # Reproject if needed
        if gdf.crs and gdf.crs.to_string() != 'EPSG:4326':
            point_gdf = point_gdf.to_crs(gdf.crs)
        
        # Apply buffer if specified
        if buffer_meters > 0:
            # Project to metric CRS for buffering
            metric_crs = 'EPSG:3857'  # Web Mercator
            point_gdf = point_gdf.to_crs(metric_crs)
            point_gdf['geometry'] = point_gdf.buffer(buffer_meters)
            point_gdf = point_gdf.to_crs(gdf.crs)
        
        # Spatial query
        mask = gdf.intersects(point_gdf.geometry.iloc[0])
        results = gdf[mask]
        
        print(f"🔍 Found {len(results)} features near ({lon}, {lat})")
        return results.to_dict('records')
    
    async def query_vector_by_bbox(
        self, 
        file_path: str, 
        bbox: Tuple[float, float, float, float]
    ) -> List[Dict[str, Any]]:
        """
        Query vector features within a bounding box
        
        Args:
            file_path: Path to vector file
            bbox: Bounding box (minx, miny, maxx, maxy)
            
        Returns:
            List of features intersecting the bbox
        """
        gdf = gpd.read_file(file_path)
        
        # Create bbox geometry
        bbox_geom = box(*bbox)
        bbox_gdf = gpd.GeoDataFrame([{'geometry': bbox_geom}], crs='EPSG:4326')
        
        # Reproject if needed
        if gdf.crs and gdf.crs.to_string() != 'EPSG:4326':
            bbox_gdf = bbox_gdf.to_crs(gdf.crs)
        
        # Spatial query
        mask = gdf.intersects(bbox_gdf.geometry.iloc[0])
        results = gdf[mask]
        
        print(f"🔍 Found {len(results)} features in bbox")
        return results.to_dict('records')
    
    # ==================== ANALYTICS ====================
    
    async def compute_raster_statistics(
        self, 
        file_path: str, 
        polygon: Optional[Polygon] = None
    ) -> Dict[str, float]:
        """
        Compute statistics for a raster dataset
        
        Args:
            file_path: Path to raster file
            polygon: Optional polygon to clip statistics to
            
        Returns:
            Dictionary of statistics (min, max, mean, std, etc.)
        """
        with rasterio.open(file_path) as src:
            data = src.read(1)
            
            if polygon:
                # Mask data to polygon
                from rasterio.mask import mask
                masked, _ = mask(src, [polygon], crop=True)
                data = masked[0]
            
            stats = {
                "min": float(np.nanmin(data)),
                "max": float(np.nanmax(data)),
                "mean": float(np.nanmean(data)),
                "median": float(np.nanmedian(data)),
                "std": float(np.nanstd(data)),
                "percentile_25": float(np.nanpercentile(data, 25)),
                "percentile_75": float(np.nanpercentile(data, 75))
            }
            
            return stats
    
    async def get_elevation_profile(
        self, 
        dem_path: str, 
        points: List[Tuple[float, float]]
    ) -> List[Dict[str, Any]]:
        """
        Get elevation profile along a path
        
        Args:
            dem_path: Path to Digital Elevation Model (DEM) raster
            points: List of (lon, lat) points defining the path
            
        Returns:
            List of elevation values along the path
        """
        results = []
        
        for lon, lat in points:
            elev = await self.read_raster_at_point(dem_path, lon, lat)
            results.append({
                "lon": lon,
                "lat": lat,
                "elevation": elev
            })
        
        return results
    
    # ==================== EXPORT ====================
    
    async def export_to_geojson(
        self, 
        gdf: gpd.GeoDataFrame, 
        output_path: str
    ) -> str:
        """Export GeoDataFrame to GeoJSON"""
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"💾 Exported to GeoJSON: {output_path}")
        return output_path
    
    async def export_raster_to_cog(
        self, 
        data: np.ndarray, 
        metadata: RasterMetadata, 
        output_path: str
    ) -> str:
        """Export raster to Cloud Optimized GeoTIFF (COG)"""
        # Create GeoTIFF with proper metadata
        transform = rasterio.transform.from_gdal(*metadata.geotransform)
        
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=metadata.height,
            width=metadata.width,
            count=1,
            dtype=data.dtype,
            crs=metadata.projection,
            transform=transform,
            compress='lzw',
            tiled=True,
            blockxsize=256,
            blockysize=256
        ) as dst:
            dst.write(data, 1)
        
        print(f"💾 Exported to COG: {output_path}")
        return output_path
    
    # ==================== UTILITY ====================
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached datasets"""
        return {
            "raster_cache": list(self._raster_cache.keys()),
            "vector_cache": list(self._vector_cache.keys()),
            "cache_dir": str(self.cache_dir)
        }
    
    def clear_cache(self):
        """Clear all cached datasets"""
        self._raster_cache.clear()
        self._vector_cache.clear()
        print("🗑️  Cache cleared")


# Example usage
if __name__ == "__main__":
    async def demo():
        engine = GeospatialEngine()
        await engine.initialize()
        
        print("\n🌍 Geospatial Engine Demo")
        print("=" * 50)
        print("Engine ready for:")
        print("  - Raster data processing (satellite imagery, DEMs)")
        print("  - Vector data queries (boundaries, POIs)")
        print("  - Geospatial analytics (NDVI, terrain analysis)")
        print("  - Location-based trading signals")
        print("\nIntegration with ACTORS financial system enables:")
        print("  - Agricultural commodity trading (crop monitoring)")
        print("  - Real estate analysis (location intelligence)")
        print("  - Supply chain optimization (route analysis)")
        print("  - Climate risk assessment (environmental data)")
        print("  - Alternative data signals (satellite observations)")
    
    asyncio.run(demo())
