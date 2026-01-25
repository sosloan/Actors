# 🌍 Geospatial Data Integration Guide

## Overview

The ACTORS Geospatial Integration provides GDAL-powered geospatial data processing capabilities for enhanced financial trading decisions. This integration enables the use of satellite imagery, geographic vector data, and spatial analysis to generate alternative data signals and location-based insights.

## 🎯 Use Cases

### 1. Agricultural Commodity Trading
**Objective**: Monitor crop health to predict agricultural commodity prices

**Data Sources**:
- Satellite imagery (Landsat, Sentinel-2, MODIS)
- Weather data (precipitation, temperature)
- Soil data

**Analysis**:
- NDVI (Normalized Difference Vegetation Index) for crop health
- EVI (Enhanced Vegetation Index)
- Time-series analysis of vegetation trends

**Trading Signals**:
- Declining NDVI → Short corn/wheat futures
- Improving NDVI → Long agricultural commodities
- Regional crop failures → Price volatility opportunities

**Example**:
```python
from core.geospatial_engine import GeospatialEngine

engine = GeospatialEngine()
await engine.initialize()

# Compute NDVI for corn belt region
ndvi_result = await engine.compute_ndvi(
    red_band='sentinel2_red_band.tif',
    nir_band='sentinel2_nir_band.tif'
)

# Generate trading signal
if ndvi_result['stats']['mean'] < 0.4:
    signal = TradingSignal(
        action='SHORT',
        asset='CORN_FUTURES',
        confidence=0.85,
        reason=f"Poor crop health: NDVI {ndvi_result['stats']['mean']:.2f}"
    )
```

### 2. Real Estate Portfolio Optimization
**Objective**: Optimize commercial real estate investments using location intelligence

**Data Sources**:
- Property boundaries (parcels, zoning)
- Infrastructure (transit, roads, utilities)
- Demographic data
- Points of interest (retail, schools, hospitals)

**Analysis**:
- Proximity analysis (distance to transit, amenities)
- Spatial queries (properties in target zones)
- Density analysis (population, business density)

**Trading Signals**:
- High-growth areas → Invest in REITs/properties
- Infrastructure improvements → Early investment opportunities
- Declining areas → Divest holdings

**Example**:
```python
# Load property data
properties = await engine.load_vector('city_properties.geojson')

# Query properties near new transit station
nearby_props = await engine.query_vector_by_location(
    'city_properties.geojson',
    lon=-122.4194,
    lat=37.7749,
    buffer_meters=1000
)

# Rank by investment potential
for prop in nearby_props:
    prop['score'] = calculate_investment_score(prop)
    
best_investments = sorted(nearby_props, key=lambda x: x['score'], reverse=True)[:10]
```

### 3. Supply Chain & Logistics Optimization
**Objective**: Optimize transportation routes and warehouse locations

**Data Sources**:
- Digital Elevation Models (DEM)
- Road networks
- Facility locations
- Traffic data

**Analysis**:
- Elevation profiles for route optimization
- Terrain analysis for site selection
- Accessibility analysis

**Trading Signals**:
- Route efficiency improvements → Cost savings
- Strategic warehouse placement → Competitive advantage
- Logistics bottlenecks → Supply chain risk assessment

**Example**:
```python
# Analyze route elevation profile
route_points = [(lon1, lat1), (lon2, lat2), (lon3, lat3)]
profile = await engine.get_elevation_profile('dem.tif', route_points)

# Calculate fuel cost impact
elevations = [p['elevation'] for p in profile]
elevation_gain = sum(max(0, elevations[i] - elevations[i-1]) for i in range(1, len(elevations)))

fuel_cost_impact = elevation_gain * FUEL_COST_PER_METER
```

### 4. Climate Risk Assessment
**Objective**: Assess climate-related risks for insurance and portfolio management

**Data Sources**:
- Climate models (temperature, precipitation)
- Sea level rise projections
- Flood risk maps
- Historical disaster data

**Analysis**:
- Risk exposure mapping
- Trend analysis (temperature, precipitation)
- Vulnerability assessment

**Trading Signals**:
- High climate risk areas → Adjust insurance pricing
- Portfolio exposure → Hedge climate risks
- Emerging risks → Early warning signals

### 5. Alternative Data Signals
**Objective**: Generate leading economic indicators from satellite observations

**Data Sources**:
- Nighttime lights imagery
- Parking lot occupancy (vehicle counting)
- Shipping activity (port traffic)
- Construction activity

**Analysis**:
- Change detection (activity trends)
- Anomaly detection (unusual patterns)
- Time-series analysis

**Trading Signals**:
- Declining nighttime lights → Economic slowdown
- Parking lot fullness → Retail activity
- Port congestion → Supply chain issues

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                   ACTORS Trading System                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │ Trading      │    │  Portfolio   │                  │
│  │ Agents       │◄───┤  Agents      │                  │
│  └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                           │
│         └───────┬───────────┘                           │
│                 ▼                                       │
│      ┌────────────────────┐                            │
│      │ Geospatial API     │                            │
│      │ (Flask REST)       │                            │
│      └──────────┬─────────┘                            │
│                 │                                       │
│                 ▼                                       │
│      ┌────────────────────┐                            │
│      │ Geospatial Engine  │                            │
│      │ (GDAL/Rasterio)    │                            │
│      └──────────┬─────────┘                            │
│                 │                                       │
│         ┌───────┴────────┐                             │
│         ▼                ▼                             │
│  ┌──────────┐    ┌──────────┐                          │
│  │  Raster  │    │  Vector  │                          │
│  │  Data    │    │  Data    │                          │
│  └──────────┘    └──────────┘                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Storage Integration

The geospatial system integrates with the ACTORS multi-tier database architecture:

- **L0 (Hot State)**: Frequently accessed geospatial features (NumPy arrays)
- **L1 (Rollback)**: Not typically used for geospatial data
- **L2 (Analytics)**: Spatial queries and analytics (DuckDB + Parquet)
- **L3 (Global Sync)**: Not typically used for geospatial data

**Geospatial Cache**: `/tmp/geospatial_cache` for temporary raster/vector files

## 📡 API Reference

### Raster Endpoints

#### `POST /api/geo/raster/load`
Load and analyze a raster dataset.

**Request**:
```json
{
    "file_path": "/path/to/raster.tif",
    "cache_key": "optional_cache_key"
}
```

**Response**:
```json
{
    "metadata": {
        "width": 1000,
        "height": 1000,
        "bands": 1,
        "projection": "EPSG:4326",
        "bounds": [-122.5, 37.5, -122.0, 38.0]
    },
    "stats": {
        "min": 0.1,
        "max": 0.9,
        "mean": 0.55,
        "std": 0.15
    },
    "data_shape": [1000, 1000]
}
```

#### `POST /api/geo/raster/point-query`
Query raster value at a specific point.

**Request**:
```json
{
    "file_path": "/path/to/raster.tif",
    "lon": -122.4194,
    "lat": 37.7749
}
```

**Response**:
```json
{
    "lon": -122.4194,
    "lat": 37.7749,
    "value": 0.65
}
```

#### `POST /api/geo/raster/ndvi`
Compute NDVI (Normalized Difference Vegetation Index).

**Request**:
```json
{
    "red_band": "/path/to/red.tif",
    "nir_band": "/path/to/nir.tif"
}
```

**Response**:
```json
{
    "metadata": {...},
    "stats": {
        "min": -0.1,
        "max": 0.9,
        "mean": 0.65,
        "vegetation_cover_pct": 75.5
    },
    "interpretation": {
        "vegetation_cover_pct": 75.5,
        "health_rating": "Good"
    }
}
```

### Vector Endpoints

#### `POST /api/geo/vector/load`
Load and analyze a vector dataset.

#### `POST /api/geo/vector/location-query`
Query vector features at or near a location.

#### `POST /api/geo/vector/bbox-query`
Query vector features within a bounding box.

### Analytics Endpoints

#### `POST /api/geo/analytics/elevation-profile`
Get elevation profile along a path.

### Utility Endpoints

#### `GET /api/geo/status`
Get API status and cache information.

#### `POST /api/geo/cache/clear`
Clear all cached datasets.

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Install GDAL and geospatial libraries
pip install GDAL==3.8.3 rasterio==1.3.9 geopandas==0.14.1 shapely==2.0.2
```

**Note**: GDAL can be tricky to install. If you encounter issues:

```bash
# On Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev
pip install GDAL==$(gdal-config --version)

# On macOS
brew install gdal
pip install GDAL==$(gdal-config --version)

# On Windows
# Use OSGeo4W or conda:
conda install -c conda-forge gdal rasterio geopandas
```

### 2. Verify Installation

```bash
python examples/geospatial_demo.py
```

### 3. Start Geospatial API

```bash
python apis/geospatial_api.py
```

The API will start on `http://localhost:5004`.

### 4. Test API

```bash
# Check API status
curl http://localhost:5004/api/geo/status

# Get API info
curl http://localhost:5004/api/geo
```

### 5. Integrate with Trading Agents

```python
import requests

# Query geospatial data from your trading agent
response = requests.post('http://localhost:5004/api/geo/raster/ndvi', json={
    'red_band': '/path/to/red.tif',
    'nir_band': '/path/to/nir.tif'
})

ndvi_data = response.json()

# Use geospatial insights for trading decisions
if ndvi_data['stats']['mean'] < 0.4:
    # Poor crop health - short agricultural commodities
    execute_trade('SHORT', 'CORN_FUTURES')
```

## 📊 Data Sources

### Free and Open Data

1. **Satellite Imagery**:
   - [USGS EarthExplorer](https://earthexplorer.usgs.gov/) - Landsat, ASTER, SRTM
   - [Copernicus Open Access Hub](https://scihub.copernicus.eu/) - Sentinel-2, Sentinel-1
   - [NASA Earthdata](https://earthdata.nasa.gov/) - MODIS, various datasets

2. **Vector Data**:
   - [OpenStreetMap](https://www.openstreetmap.org/) - Global map data
   - [Natural Earth](https://www.naturalearthdata.com/) - Cultural/physical vectors
   - [US Census TIGER](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) - US boundaries

3. **Elevation Data**:
   - [SRTM](https://www2.jpl.nasa.gov/srtm/) - 30m global DEM
   - [ASTER GDEM](https://asterweb.jpl.nasa.gov/gdem.asp) - 30m global DEM
   - [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) - US high-res DEM

### Commercial Data

1. **Planet Labs** - Daily satellite imagery
2. **Maxar** - High-resolution imagery
3. **Orbital Insight** - Geospatial analytics products

## 🧪 Testing

Run the test suite:

```bash
pytest tests/test_geospatial_engine.py -v
```

**Note**: Tests require GDAL to be installed. They will be skipped if GDAL is not available.

## 🔧 Configuration

Configure geospatial settings in `database/config.py`:

```python
from database.config import GeospatialConfig

config = GeospatialConfig(
    cache_dir="/custom/cache/dir",
    max_raster_size_mb=1000,
    enable_caching=True,
    default_projection="EPSG:4326",
    enable_compression=True,
    tile_size=512
)
```

## 📚 Resources

- **GDAL Documentation**: https://gdal.org/en/latest/
- **Rasterio**: https://rasterio.readthedocs.io/
- **GeoPandas**: https://geopandas.org/
- **Shapely**: https://shapely.readthedocs.io/

## 🎯 Next Steps

1. **Acquire Data**: Download sample satellite imagery or vector data
2. **Process Data**: Use the geospatial API to analyze data
3. **Generate Signals**: Integrate geospatial insights into trading agents
4. **Backtest**: Validate geospatial signals against historical market data
5. **Deploy**: Integrate into production trading system

## 💡 Tips

- **Start Small**: Begin with a small region/dataset to test workflows
- **Cloud Optimized**: Use Cloud Optimized GeoTIFFs (COG) for better performance
- **Caching**: Enable caching for frequently accessed datasets
- **Projections**: Always check coordinate reference systems (CRS)
- **Memory**: Large rasters can be memory-intensive; use tiling for big datasets

## 🌍 Conclusion

The Geospatial Integration brings powerful location-based analytics to ACTORS, enabling:
- Alternative data signals from satellite observations
- Location intelligence for real estate and logistics
- Environmental monitoring for risk assessment
- Comprehensive spatial analysis for trading decisions

Leverage geospatial data to gain an edge in financial markets!
