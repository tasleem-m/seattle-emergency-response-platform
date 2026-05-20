# Seattle 911 Emergency Response Analytics Pipeline
A near real-time emergency response analytics platform enriched with weather and demographic data to analyze demand patterns, geographic equity, and external drivers.

Presentation: https://canva.link/k0jjff27bx8w2yb

## Project Overview

This project is an end-to-end data engineering and analytics pipeline that analyzes Seattle Fire 911 emergency call patterns using weather and census enrichment.

The pipeline ingests emergency incident data, historical hourly weather observations, census demographics, and census tract boundaries into Snowflake. The data is then transformed with dbt using a medallion architecture pattern to produce analytics-ready gold models for operational, spatial, demographic, and weather impact analysis. Apache Airflow orchestrates ingestion, Snowflake loading, dbt transformations, and automated data quality validation across the full pipeline lifecycle.

The goal of this project is to understand how emergency call volume varies across time, geography, population density, and weather conditions. The final warehouse supports analysis such as emergency call volume trends, tract-level hotspots, calls per capita, and weather-related incident patterns.

## Architecture

The pipeline follows a medallion-style architecture using Snowflake and dbt.

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
      AWS S3 Bronze Layer
     (Partitioned Parquet)
            │
            ▼
     Apache Airflow Orchestration
   (Scheduling & Pipeline Control)
            │
            ▼
    Snowflake BRONZE Layer
     (Raw Source Storage)
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
  Analytics & Geospatial Insights
```

## Datasets
<details>     
<summary>
            
**Seattle Fire 911 Calls**
</summary>

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
</details>
<details>     
<summary>
            
**NOAA GHCNh Hourly Weather Data**
</summary>

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
</details>
<details>     
<summary>
            
**U.S. Census ACS Demographics**
</summary>

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
</details>
<details>     
<summary>
            
**Census TIGER/Line Tracts**
</summary>

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
</details>

## Tech Stack

### Data Ingestion
- **Python** — Core ingestion and orchestration scripting
- **Polars** — High-performance dataframe processing and transformation
- **AWS S3** — Bronze-layer parquet storage and staging
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

### Workflow Orchestration
- **Apache Airflow**

Implemented use cases:
- Scheduled ingestion pipelines
- Automated Snowflake bronze loading
- Automated dbt model execution
- Automated dbt testing and validation
- End-to-end pipeline orchestration
- DAG-based workflow monitoring and retries

Airflow orchestrates:
1. API ingestion and S3 bronze uploads
2. Snowflake bronze-layer loading
3. dbt silver and gold model execution
4. dbt testing and validation

## Medallion Architecture

The warehouse follows a medallion architecture pattern to separate raw ingestion, standardized transformations, reusable intermediate logic, and business-ready analytics.

This approach improves:
- Data quality
- Reusability
- Lineage clarity
- Debugging
- Analytical consistency

---

<details>     
<summary>
            
**BRONZE Layer**
</summary>

The BRONZE layer stores ingested source data with minimal transformation.

Objectives:
- Preserve source fidelity
- Support reproducibility
- Retain semi-structured source records

Characteristics:
- Partitioned parquet storage in AWS S3
- Automated Snowflake bronze ingestion via Airflow
- Incremental Snowflake COPY INTO loading

Core tables:
- `BRZ_911_CALLS`
- `BRZ_WEATHER`
- `BRZ_CENSUS`
- `BRZ_CENSUS_TRACTS`
</details>
<details>     
<summary>
            
**SILVER Layer**
</summary>

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
</details>
<details>     
<summary>
            
**INTERMEDIATE Layer**
</summary>

The INTERMEDIATE layer contains reusable transformation logic and canonicalized datasets shared across downstream marts.

Transformations include:
- NOAA weather observation deduplication
- Canonical hourly weather selection

Core models:
- `INT_WEATHER_HOURLY`

This layer reduces duplicated business logic across gold models and improves transformation maintainability.
</details>
<details>     
<summary>
            
**GOLD Layer**
</summary>

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
</details>

## Pipeline Orchestration

Apache Airflow orchestrates the end-to-end pipeline execution and coordinates ingestion, warehouse loading, transformation, and validation workflows.

The Airflow DAG performs the following steps:

1. Execute Python ingestion pipelines
2. Retrieve Seattle 911, NOAA weather, and Census datasets
3. Store partitioned parquet files in AWS S3 bronze storage
4. Load new parquet files into Snowflake bronze tables
5. Execute dbt silver transformations
6. Execute dbt gold analytical marts
7. Run dbt data quality tests

## Key Models

The GOLD layer contains business-ready analytical marts used for operational and spatial analysis.

---

<details>     
<summary>
            
**`GLD_INCIDENT_ENRICHED`**
</summary>

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
</details>
<details>     
<summary>
            
**`GLD_SPATIAL_HOTSPOTS`**
</summary>

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
</details>
<details>     
<summary>
            
**`GLD_WEATHER_IMPACT`**
</summary>

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
</details>
<details>     
<summary>
            
**`GLD_CALL_VOLUME_TRENDS`**
</summary>

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
</details>
<details>     
<summary>
            
**`GLD_CALLS_PER_CAPITA`**
</summary>

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
</details>

## Geospatial Analytics

Geospatial enrichment is a core component of the pipeline and enables neighborhood-level operational analysis across Seattle.

The project uses Snowflake geospatial functions and census tract polygon boundaries to spatially enrich emergency incidents with demographic context.

---

<details>     
<summary>
            
**Incident Geospatial Enrichment**
</summary>

Emergency incidents are converted into Snowflake `GEOGRAPHY` point objects using latitude and longitude coordinates.

Example:

```sql
ST_POINT(longitude, latitude)
```
</details>
<details>     
<summary>
            
**Census Tract Polygon Processing**
</summary>

Census TIGER/Line tract geometries were loaded into Snowflake and converted into native GEOGRAPHY polygon objects. This enabled tract-level spatial joins directly within Snowflake.

Example:

```sql
TO_GEOGRAPHY(geometry)
```
</details>
<details>     
<summary>
            
**Point-in-Polygon Spatial Joins**
</summary>

Emergency incidents were spatially matched to census tracts using Snowflake's ST_CONTAINS function. This enrichment process attached Census tract GEOIDs, Population metrics, Median household income, Demographic context to each emergency incident.

Example:

```sql
ST_CONTAINS(
    tract_geography,
    incident_geography
)
```
</details>
<details>     
<summary>
            
**Spatial Analytics Use Cases**
</summary>

The geospatial enrichment layer enables:

- Census tract hotspot analysis
- Calls per capita analysis
- Neighborhood operational burden analysis
- Demographic incident normalization
- Geographic trend visualization
- Spatial clustering and mapping
</details>
<details>     
<summary>
            
**Spatially Enriched Gold Models**
</summary>

Key geospatially enriched models include:

- GLD_INCIDENT_ENRICHED
- GLD_SPATIAL_HOTSPOTS
- GLD_CALLS_PER_CAPITA

These models support operational and demographic analysis at the census tract level.
</details>

## Data Quality Handling

Several data quality and standardization strategies were implemented throughout the pipeline to improve analytical reliability and consistency.

---

<details>     
<summary>
            
**Census Sentinel Value Normalization**
</summary>

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
</details>
<details>     
<summary>
            
**Weather Observation Deduplication**
</summary> 

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
</details>
<details>     
<summary>
            
**Coordinate Fallback Handling**
</summary>

Some Seattle Fire incident records contained missing top-level latitude and longitude values while still preserving valid GeoJSON report location coordinates.

Fallback logic was implemented using COALESCE to recover coordinates from GeoJSON geometry fields. This improved geospatial completeness and reduced null geographic records.

Example:

```sql
COALESCE(
    raw_latitude,
    report_location:coordinates[1]::FLOAT
)
```
</details>
<details>     
<summary>
            
**Timestamp Standardization**
</summary>

Source systems contained multiple timestamp formats across APIs and raw ingestion layers.

Timestamps were standardized using Snowflake timestamp conversion functions. This enabled reliable temporal joins, hourly weather enrichment, monthly trend aggregation, and consistent time-series analysis.

Example:

```sql
TRY_TO_TIMESTAMP_NTZ()
```
</details>
<details>     
<summary>
            
**Geospatial Standardization**
</summary>

Census tract polygon geometries and incident coordinates were standardized into Snowflake GEOGRAPHY objects. This enabled accurate point-in-polygon enrichment and tract-level spatial analysis.

Example:

```sql
TO_GEOGRAPHY(geometry)

ST_POINT(longitude, latitude)
```
</details>
<details>     
<summary>
            
**dbt Testing and Validation**
</summary>

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
</details>
<details>     
<summary>
            
**Workflow Reliability & Orchestration**
</summary>

Apache Airflow was used to orchestrate ingestion, warehouse loading, transformation, and testing workflows across the pipeline.

Airflow DAGs provided:
- Centralized workflow scheduling
- Dependency management
- Retry handling
- Execution monitoring
- End-to-end pipeline observability

This orchestration layer improved operational reliability and automated the full medallion pipeline lifecycle.

Example orchestration flow:

```text
Python Ingestion
        ↓
AWS S3 Bronze
        ↓
Snowflake Bronze Load
        ↓
dbt Silver Models
        ↓
dbt Gold Models
        ↓
dbt Tests
```
</details>
