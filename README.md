# Seattle 911 Emergency Response Analytics Pipeline
A near real-time emergency response analytics platform enriched with weather and demographic data to analyze demand patterns, geographic equity, and external drivers.

## Project Overview

This project is an end-to-end data engineering and analytics pipeline that analyzes Seattle Fire 911 emergency call patterns using weather and census enrichment.

The pipeline ingests emergency incident data, historical hourly weather observations, census demographics, and census tract boundaries into Snowflake. The data is then transformed with dbt using a medallion architecture pattern to produce analytics-ready gold models for operational, spatial, demographic, and weather impact analysis.

The goal of this project is to understand how emergency call volume varies across time, geography, population density, and weather conditions. The final warehouse supports analysis such as emergency call volume trends, tract-level hotspots, calls per capita, and weather-related incident patterns.

## Architecture

The pipeline follows a medallion-style architecture using Snowflake and dbt.

### Data Flow

```text
Seattle Fire 911 API
NOAA GHCNh Weather Data
U.S. Census ACS Data
Census TIGER/Line Tracts
            │
            ▼
     Python Ingestion Layer
   (Polars, GeoPandas, Requests)
            │
            ▼
      Snowflake BRONZE Layer
            │
            ▼
      dbt SILVER Models
  (Cleaning, Typing, Standardization)
            │
            ▼
   dbt INTERMEDIATE Models
    (Deduplication & Canonicalization)
            │
            ▼
       dbt GOLD Models
 (Analytics & Business Metrics)
            │
            ▼
        Visualization Layer
   (Planned: Streamlit / Plotly)
```

## Datasets

### Seattle Fire 911 Calls

The Seattle Fire 911 Calls dataset contains emergency response incidents from the Seattle Fire Department, including incident type, timestamp, address, and geographic coordinates.

Key fields:
- Incident number
- Incident type
- Incident timestamp
- Address
- Latitude / longitude
- GeoJSON report location

Use cases:
- Emergency response trend analysis
- Spatial hotspot detection
- Temporal demand analysis
- Weather correlation analysis

Source:
- Seattle Open Data API (Socrata)

---

### NOAA GHCNh Hourly Weather Data

The NOAA Global Historical Climatology Network Hourly (GHCNh) dataset provides historical hourly weather observations from Seattle-Tacoma International Airport.

Key fields:
- Temperature
- Dew point
- Relative humidity
- Wind speed and direction
- Visibility
- Precipitation
- Weather conditions

Use cases:
- Weather impact analysis
- Incident correlation with precipitation and visibility
- Seasonal operational trend analysis

Source:
- NOAA National Centers for Environmental Information (NCEI)

Station used:
- `USW00024233` — Seattle Tacoma Airport

---

### U.S. Census ACS Demographics

American Community Survey (ACS) demographic data was used to enrich incidents with socioeconomic context at the census tract level.

Key fields:
- Total population
- Median household income
- Census tract GEOID

Use cases:
- Calls per capita analysis
- Demographic normalization
- Socioeconomic hotspot analysis

Source:
- U.S. Census Bureau API

---

### Census TIGER/Line Tracts

Census TIGER/Line tract shapefiles provide polygon boundaries for census tracts used in geospatial enrichment.

Key fields:
- Census tract GEOID
- Polygon geometry
- Tract centroid coordinates

Use cases:
- Point-in-polygon spatial joins
- Incident-to-tract enrichment
- Geographic hotspot analysis

Source:
- U.S. Census Bureau TIGER/Line Shapefiles

## Tech Stack

### Data Ingestion
- **Python** — Core ingestion and orchestration scripting
- **Polars** — High-performance dataframe processing and transformation
- **GeoPandas** — Geospatial shapefile processing and geometry handling
- **Requests** — API and HTTP data retrieval

---

### Data Warehouse
- **Snowflake** — Cloud data warehouse for storage, transformation, and geospatial analytics

Snowflake features used:
- Semi-structured VARIANT handling
- GEOGRAPHY spatial objects
- Spatial functions (`ST_POINT`, `ST_CONTAINS`)
- Window functions
- Analytical aggregations

---

### Data Transformation
- **dbt** — Transformation orchestration, testing, documentation, and lineage management

dbt features used:
- Medallion architecture modeling
- Incremental transformations
- Model testing
- Documentation generation
- Reusable intermediate models

---

### Geospatial Analytics
- **Snowflake Geospatial Functions**
  - `ST_POINT`
  - `ST_CONTAINS`
  - `TO_GEOGRAPHY`

Used for:
- Point-in-polygon joins
- Census tract enrichment
- Spatial hotspot analysis

---

### Planned Orchestration
- **Apache Airflow** *(planned)*

Planned use cases:
- Scheduled ingestion pipelines
- Automated dbt runs and tests
- End-to-end workflow orchestration

---

### Planned Visualization
- **Streamlit** *(planned)*
- **Plotly** *(planned)*

Planned dashboards:
- Incident trend analysis
- Spatial hotspot mapping
- Weather impact visualization
- Calls per capita analysis

## Medallion Architecture

The warehouse follows a medallion architecture pattern to separate raw ingestion, standardized transformations, reusable intermediate logic, and business-ready analytics.

This approach improves:
- Data quality
- Reusability
- Lineage clarity
- Debugging
- Analytical consistency

---

### BRONZE Layer

The BRONZE layer stores ingested source data with minimal transformation.

Objectives:
- Preserve source fidelity
- Support reproducibility
- Retain semi-structured source records

Characteristics:
- JSON and VARIANT ingestion
- Minimal type casting
- Append-oriented ingestion patterns

Core tables:
- `BRZ_911_CALLS`
- `BRZ_WEATHER`
- `BRZ_CENSUS`
- `BRZ_CENSUS_TRACTS`

---

### SILVER Layer

The SILVER layer standardizes raw data into clean domain entities.

Transformations include:
- Data type casting
- Timestamp normalization
- Geospatial object creation
- Coordinate fallback handling
- Census sentinel value normalization
- Quality code preservation

Core models:
- `SLV_911_CALLS`
- `SLV_WEATHER`
- `SLV_CENSUS`
- `SLV_CENSUS_TRACTS`

Example transformations:
- `ST_POINT(longitude, latitude)` geospatial conversion
- GeoJSON coordinate fallback logic
- Census null normalization using `NULLIF`
- Weather observation standardization

---

### INTERMEDIATE Layer

The INTERMEDIATE layer contains reusable transformation logic and canonicalized datasets shared across downstream marts.

Transformations include:
- NOAA weather observation deduplication
- Canonical hourly weather selection

Core models:
- `INT_WEATHER_HOURLY`

This layer reduces duplicated business logic across gold models and improves transformation maintainability.

---

### GOLD Layer

The GOLD layer contains analytics-ready marts designed for operational, demographic, weather, and spatial analysis.

Core models:
- `GLD_INCIDENT_ENRICHED`
- `GLD_SPATIAL_HOTSPOTS`
- `GLD_WEATHER_IMPACT`
- `GLD_CALL_VOLUME_TRENDS`
- `GLD_CALLS_PER_CAPITA`

Key analytical capabilities:
- Point-in-polygon tract enrichment
- Calls per capita normalization
- Weather impact analysis
- Temporal trend analysis
- Spatial hotspot detection
- Demographic enrichment

## Key Models

### `GLD_INCIDENT_ENRICHED`

The central fact table of the warehouse.

This model enriches Seattle Fire 911 incidents with:
- Census tract geography
- Demographic metrics
- Hourly weather observations

Key enrichments:
- Spatial tract assignment using `ST_CONTAINS`
- Weather joins using hourly timestamp alignment
- Demographic joins using tract GEOID and census year

Key metrics and dimensions:
- Incident type
- Incident timestamp
- Census tract identifiers
- Population
- Median household income
- Temperature
- Precipitation
- Visibility
- Weather conditions

Purpose:
- Foundation for downstream analytical marts
- Unified operational analytics dataset
- Spatial and environmental enrichment layer

---

### `GLD_SPATIAL_HOTSPOTS`

Aggregates emergency incidents by census tract and census year to identify geographic hotspots.

Key metrics:
- Total incidents
- Incidents per 1,000 residents
- Average temperature during incidents
- Average precipitation
- Most common incident type

Purpose:
- Spatial hotspot analysis
- Neighborhood-level operational burden analysis
- Geographic demand normalization

Key feature:
- Population-normalized incident rates for fair geographic comparison

---

### `GLD_WEATHER_IMPACT`

Daily aggregation of incidents and associated weather conditions.

Key metrics:
- Total daily incidents
- Average temperature
- Relative humidity
- Visibility
- Wind speed
- Total precipitation
- Dominant weather condition

Purpose:
- Environmental and operational correlation analysis
- Weather impact trend analysis
- Seasonal incident pattern analysis

---

### `GLD_CALL_VOLUME_TRENDS`

Monthly operational trend analysis by incident type.

Key metrics:
- Total incidents
- Average daily incidents
- Rolling three-month incident averages

Purpose:
- Long-term operational trend analysis
- Incident seasonality analysis
- Incident type trend monitoring

Key feature:
- Rolling average smoothing for operational trend analysis

---

### `GLD_CALLS_PER_CAPITA`

Demographically normalized emergency incident burden analysis by census tract and year.

Key metrics:
- Total incidents
- Incidents per 1,000 residents
- Incident burden rank
- Incident burden quintile

Purpose:
- Socioeconomic demand analysis
- Public-sector operational burden analysis
- Geographic equity analysis

Key feature:
- Population-normalized tract ranking using window functions

## Geospatial Analytics

Geospatial enrichment is a core component of the pipeline and enables neighborhood-level operational analysis across Seattle.

The project uses Snowflake geospatial functions and census tract polygon boundaries to spatially enrich emergency incidents with demographic context.

---

### Incident Geospatial Enrichment

Emergency incidents are converted into Snowflake `GEOGRAPHY` point objects using latitude and longitude coordinates.

Example:

```sql
ST_POINT(longitude, latitude)
```

### Census Tract Polygon Processing

Census TIGER/Line tract geometries were loaded into Snowflake and converted into native GEOGRAPHY polygon objects. This enabled tract-level spatial joins directly within Snowflake.

Example:

```sql
TO_GEOGRAPHY(geometry)
```

### Point-in-Polygon Spatial Joins

Emergency incidents were spatially matched to census tracts using Snowflake's ST_CONTAINS function. This enrichment process attached Census tract GEOIDs, Population metrics, Median household income, Demographic context to each emergency incident.

Example:

```sql
ST_CONTAINS(
    tract_geography,
    incident_geography
)
```

### Spatial Analytics Use Cases

The geospatial enrichment layer enables:

- Census tract hotspot analysis
- Calls per capita analysis
- Neighborhood operational burden analysis
- Demographic incident normalization
- Geographic trend visualization
- Spatial clustering and mapping

### Spatially Enriched Gold Models

Key geospatially enriched models include:

- GLD_INCIDENT_ENRICHED
- GLD_SPATIAL_HOTSPOTS
- GLD_CALLS_PER_CAPITA

These models support operational and demographic analysis at the census tract level.

## Data Quality Handling

Several data quality and standardization strategies were implemented throughout the pipeline to improve analytical reliability and consistency.

---

### Census Sentinel Value Normalization

Certain Census API fields contained sentinel values representing unavailable or suppressed data.

Example:
- `-666666666`

These values were normalized to SQL `NULL` values using `NULLIF` to prevent invalid analytical calculations. This ensured demographic aggregations and per-capita metrics remained analytically valid.

Example:

```sql id="cnrqqh"
NULLIF(
    raw_data:B19013_001E::INTEGER,
    -666666666
)
```

### Weather Observation Deduplication

NOAA GHCNh hourly weather data can contain multiple observations within the same hour.

To create canonical hourly observations, weather records were deduplicated using window functions and the most recent observation within each hour was retained. This prevented duplicate joins and inconsistent weather enrichment downstream.

Example:

```sql
QUALIFY ROW_NUMBER() OVER (

    PARTITION BY
        station_id,
        DATE_TRUNC('hour', observed_at_utc)

    ORDER BY observed_minute DESC

) = 1
```

### Coordinate Fallback Handling

Some Seattle Fire incident records contained missing top-level latitude and longitude values while still preserving valid GeoJSON report location coordinates.

Fallback logic was implemented using COALESCE to recover coordinates from GeoJSON geometry fields. This improved geospatial completeness and reduced null geographic records.

Example:

```sql
COALESCE(
    raw_latitude,
    report_location:coordinates[1]::FLOAT
)
```

### Timestamp Standardization

Source systems contained multiple timestamp formats across APIs and raw ingestion layers.

Timestamps were standardized using Snowflake timestamp conversion functions. This enabled reliable temporal joins, hourly weather enrichment, monthly trend aggregation, and consistent time-series analysis.

Example:

```sql
TRY_TO_TIMESTAMP_NTZ()
```

### Geospatial Standardization

Census tract polygon geometries and incident coordinates were standardized into Snowflake GEOGRAPHY objects. This enabled accurate point-in-polygon enrichment and tract-level spatial analysis.

Example:

```sql
TO_GEOGRAPHY(geometry)

ST_POINT(longitude, latitude)
```

### dbt Testing and Validation

dbt tests were implemented across silver and gold models to validate:

- Non-null business keys
- Temporal fields
- Geographic identifiers
- Analytical grain consistency
- Composite uniqueness constraints

Examples:

- not_null
- unique

This improved model reliability and analytical trustworthiness across the warehouse.
