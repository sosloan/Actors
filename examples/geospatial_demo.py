#!/usr/bin/env python3
"""
Geospatial Data Integration Demo for ACTORS

Demonstrates how to use GDAL-powered geospatial features for:
- Alternative data integration (satellite imagery)
- Location-based trading signals
- Agricultural commodity analysis
- Real estate portfolio optimization
"""

import asyncio
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.geospatial_engine import GeospatialEngine, GDAL_AVAILABLE


async def demo_basic_capabilities():
    """Demo basic geospatial capabilities"""
    print("=" * 80)
    print("🌍 ACTORS Geospatial Integration Demo")
    print("=" * 80)
    
    if not GDAL_AVAILABLE:
        print("\n❌ GDAL not available!")
        print("Install with: pip install GDAL rasterio geopandas shapely")
        return
    
    # Initialize engine
    engine = GeospatialEngine(cache_dir="/tmp/actors_geo_demo")
    await engine.initialize()
    
    print("\n" + "=" * 80)
    print("📊 Geospatial Features for Financial Trading")
    print("=" * 80)
    
    print("\n1️⃣  AGRICULTURAL COMMODITY TRADING")
    print("   Use Case: Monitor crop health for corn/wheat futures trading")
    print("   Data Source: Satellite imagery (Landsat, Sentinel-2)")
    print("   Analysis: NDVI (Normalized Difference Vegetation Index)")
    print("   Signal: Declining vegetation health → Short agricultural futures")
    print("   Example:")
    print("     - Load NIR and Red bands from satellite imagery")
    print("     - Compute NDVI to assess crop health")
    print("     - Generate trading signals based on regional crop conditions")
    
    print("\n2️⃣  REAL ESTATE PORTFOLIO OPTIMIZATION")
    print("   Use Case: Optimize commercial real estate portfolio")
    print("   Data Source: Vector data (property boundaries, zoning)")
    print("   Analysis: Spatial queries, proximity analysis")
    print("   Signal: Property value trends by location")
    print("   Example:")
    print("     - Load property boundary data (GeoJSON/Shapefile)")
    print("     - Query properties within investment zones")
    print("     - Analyze proximity to infrastructure (transit, amenities)")
    
    print("\n3️⃣  SUPPLY CHAIN & LOGISTICS")
    print("   Use Case: Optimize transportation routes for cost reduction")
    print("   Data Source: Digital Elevation Models (DEM)")
    print("   Analysis: Elevation profiles, terrain analysis")
    print("   Signal: Route efficiency metrics")
    print("   Example:")
    print("     - Load DEM data for route planning")
    print("     - Compute elevation profiles along routes")
    print("     - Optimize fuel costs based on terrain")
    
    print("\n4️⃣  CLIMATE RISK ASSESSMENT")
    print("   Use Case: Assess climate risks for insurance/reinsurance")
    print("   Data Source: Climate rasters (temperature, precipitation)")
    print("   Analysis: Spatial statistics, trend analysis")
    print("   Signal: Risk-adjusted portfolio positioning")
    print("   Example:")
    print("     - Load climate data layers")
    print("     - Compute regional risk metrics")
    print("     - Adjust portfolio based on climate exposure")
    
    print("\n5️⃣  ALTERNATIVE DATA SIGNALS")
    print("   Use Case: Detect economic activity from satellite data")
    print("   Data Source: Nighttime lights, parking lot occupancy")
    print("   Analysis: Change detection, time series analysis")
    print("   Signal: Leading indicators of economic trends")
    print("   Example:")
    print("     - Load nighttime lights imagery")
    print("     - Detect changes in retail activity")
    print("     - Generate leading economic indicators")


async def demo_sample_workflow():
    """Demo a complete workflow with synthetic data"""
    print("\n" + "=" * 80)
    print("🔬 Sample Workflow: Creating Synthetic Geospatial Data")
    print("=" * 80)
    
    if not GDAL_AVAILABLE:
        return
    
    engine = GeospatialEngine(cache_dir="/tmp/actors_geo_demo")
    await engine.initialize()
    
    print("\n📝 Creating synthetic raster data (simulated crop field)...")
    
    # Create a synthetic NDVI raster
    width, height = 100, 100
    
    # Simulate crop field with varying health
    # Center is healthy (high NDVI), edges are stressed (low NDVI)
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Gaussian-like pattern for crop health
    distance_from_center = np.sqrt(xx**2 + yy**2)
    synthetic_ndvi = 0.8 * np.exp(-distance_from_center**2) + 0.1
    
    # Add some random variation (weather, soil quality)
    np.random.seed(42)
    noise = np.random.normal(0, 0.05, (height, width))
    synthetic_ndvi += noise
    
    # Clip to valid NDVI range [-1, 1]
    synthetic_ndvi = np.clip(synthetic_ndvi, -1, 1)
    
    print(f"   Generated {width}x{height} synthetic NDVI raster")
    print(f"   NDVI range: [{synthetic_ndvi.min():.3f}, {synthetic_ndvi.max():.3f}]")
    print(f"   Mean NDVI: {synthetic_ndvi.mean():.3f}")
    
    # Analyze crop health
    healthy_threshold = 0.6
    moderate_threshold = 0.4
    
    healthy_pct = (synthetic_ndvi > healthy_threshold).sum() / synthetic_ndvi.size * 100
    moderate_pct = ((synthetic_ndvi >= moderate_threshold) & (synthetic_ndvi <= healthy_threshold)).sum() / synthetic_ndvi.size * 100
    stressed_pct = (synthetic_ndvi < moderate_threshold).sum() / synthetic_ndvi.size * 100
    
    print(f"\n📊 Crop Health Analysis:")
    print(f"   Healthy (NDVI > {healthy_threshold}): {healthy_pct:.1f}%")
    print(f"   Moderate ({moderate_threshold} ≤ NDVI ≤ {healthy_threshold}): {moderate_pct:.1f}%")
    print(f"   Stressed (NDVI < {moderate_threshold}): {stressed_pct:.1f}%")
    
    # Generate trading signal
    print(f"\n💹 Trading Signal Generation:")
    if healthy_pct > 70:
        signal = "BULLISH - High crop health, expect strong yields"
        action = "LONG agricultural commodity futures"
    elif stressed_pct > 50:
        signal = "BEARISH - Low crop health, expect poor yields"
        action = "SHORT agricultural commodity futures"
    else:
        signal = "NEUTRAL - Mixed crop conditions"
        action = "HOLD current positions"
    
    print(f"   Signal: {signal}")
    print(f"   Action: {action}")


async def demo_integration_examples():
    """Show integration examples with ACTORS trading system"""
    print("\n" + "=" * 80)
    print("🔗 Integration with ACTORS Trading System")
    print("=" * 80)
    
    print("\n💡 Example 1: Agricultural Commodity Agent")
    print("```python")
    print("class AgriCommodityAgent:")
    print("    async def analyze_crop_conditions(self, region):")
    print("        # Load satellite imagery for region")
    print("        ndvi_data = await geospatial_engine.compute_ndvi(")
    print("            red_band='sentinel2_red.tif',")
    print("            nir_band='sentinel2_nir.tif'")
    print("        )")
    print("        ")
    print("        # Generate trading signal")
    print("        if ndvi_data['stats']['mean'] < 0.4:")
    print("            return TradingSignal(")
    print("                action='SHORT',")
    print("                asset='CORN_FUTURES',")
    print("                confidence=0.85,")
    print("                reason='Poor crop health detected via NDVI'")
    print("            )")
    print("```")
    
    print("\n💡 Example 2: Real Estate Portfolio Agent")
    print("```python")
    print("class RealEstateAgent:")
    print("    async def optimize_portfolio(self, target_city):")
    print("        # Load property data")
    print("        properties = await geospatial_engine.load_vector(")
    print("            'properties.geojson'")
    print("        )")
    print("        ")
    print("        # Query properties in high-growth zones")
    print("        bbox = [lon_min, lat_min, lon_max, lat_max]")
    print("        candidates = await geospatial_engine.query_vector_by_bbox(")
    print("            'properties.geojson', bbox")
    print("        )")
    print("        ")
    print("        # Rank by proximity to transit")
    print("        for prop in candidates:")
    print("            transit_distance = calculate_distance(prop, transit_hubs)")
    print("            prop['score'] = 1.0 / (1.0 + transit_distance)")
    print("        ")
    print("        return sorted(candidates, key=lambda x: x['score'], reverse=True)")
    print("```")
    
    print("\n💡 Example 3: Alternative Data Signal Agent")
    print("```python")
    print("class AltDataAgent:")
    print("    async def detect_retail_activity(self, retail_chain):")
    print("        # Load parking lot satellite imagery")
    print("        current = await geospatial_engine.load_raster('parking_current.tif')")
    print("        previous = await geospatial_engine.load_raster('parking_previous.tif')")
    print("        ")
    print("        # Detect change in car density (proxy for customer traffic)")
    print("        change = current['data'] - previous['data']")
    print("        activity_trend = np.mean(change)")
    print("        ")
    print("        if activity_trend > threshold:")
    print("            return TradingSignal(")
    print("                action='LONG',")
    print("                asset=f'{retail_chain}_STOCK',")
    print("                confidence=0.75,")
    print("                reason='Increased parking lot activity detected'")
    print("            )")
    print("```")


async def main():
    """Run all demos"""
    await demo_basic_capabilities()
    await demo_sample_workflow()
    await demo_integration_examples()
    
    print("\n" + "=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print("\n🚀 Next Steps:")
    print("   1. Install GDAL: pip install GDAL rasterio geopandas shapely")
    print("   2. Start Geospatial API: python apis/geospatial_api.py")
    print("   3. Test API: curl http://localhost:5004/api/geo")
    print("   4. Integrate with your trading agents")
    print("\n📚 Resources:")
    print("   - GDAL Documentation: https://gdal.org/en/latest/")
    print("   - Rasterio Tutorial: https://rasterio.readthedocs.io/")
    print("   - GeoPandas Guide: https://geopandas.org/")
    print("\n🌍 Start leveraging geospatial data for smarter trading decisions!")


if __name__ == "__main__":
    asyncio.run(main())
