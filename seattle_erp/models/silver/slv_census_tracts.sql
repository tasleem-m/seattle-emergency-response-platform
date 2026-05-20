WITH source AS (

    SELECT *
    FROM {{ source('BRONZE', 'BRZ_CENSUS_TRACTS') }}

),

renamed AS (

    SELECT

        -- geographic identifiers
        GEOID::VARCHAR AS tract_geoid,

        STATEFP::VARCHAR AS state_fips,
        COUNTYFP::VARCHAR AS county_fips,
        TRACTCE::VARCHAR AS tract_code,

        NAME::VARCHAR AS tract_name,
        NAMELSAD::VARCHAR AS tract_full_name,

        -- land/water area
        ALAND::NUMBER AS land_area_sq_meters,
        AWATER::NUMBER AS water_area_sq_meters,

        -- tract centroid
        INTPTLAT::FLOAT AS centroid_latitude,
        INTPTLON::FLOAT AS centroid_longitude,

        -- geometry
        "geometry"::VARCHAR AS tract_wkt,

        -- convert WKT polygon into Snowflake GEOGRAPHY
        TO_GEOGRAPHY("geometry") AS tract_geography,

        CURRENT_TIMESTAMP() AS transformed_at_utc

    FROM source

),

final AS (

    SELECT *

    FROM renamed

    WHERE tract_geoid IS NOT NULL

)

SELECT *
FROM final
