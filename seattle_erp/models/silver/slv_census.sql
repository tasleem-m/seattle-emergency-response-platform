WITH source AS (

    SELECT
        $1 AS bronze_data
    FROM {{ source('BRONZE', 'BRZ_CENSUS') }}

),

renamed AS (

    SELECT

        -- geographic identifiers
        bronze_data:geoid::VARCHAR AS tract_geoid,

        bronze_data:state::VARCHAR AS state_fips,
        bronze_data:county::VARCHAR AS county_fips,
        bronze_data:tract::VARCHAR AS tract_code,

        -- time dimension
        bronze_data:year::INTEGER AS census_year,

        -- demographics
        bronze_data:B01003_001E::INTEGER AS total_population,

        NULLIF(bronze_data:B19013_001E::INTEGER, -666666666) AS median_household_income,

        -- metadata
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
