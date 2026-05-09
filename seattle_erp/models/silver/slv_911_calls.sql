WITH source AS (

    SELECT
        $1 AS bronze_data
    FROM {{ source('BRONZE', 'BRZ_911_CALLS') }}

),

renamed AS (

    SELECT

        -- business key
        bronze_data:INCIDENT_NUMBER::VARCHAR AS incident_number,

        -- timestamps
        TRY_TO_TIMESTAMP_NTZ(bronze_data:DATETIME::VARCHAR) AS incident_timestamp,

        -- incident details
        bronze_data:TYPE::VARCHAR AS incident_type,
        bronze_data:ADDRESS::VARCHAR AS address,

        -- coordinates
        bronze_data:LATITUDE::FLOAT AS raw_latitude,
        bronze_data:LONGITUDE::FLOAT AS raw_longitude,

        bronze_data:REPORT_LOCATION AS report_location,

        -- ingestion metadata
        TRY_TO_TIMESTAMP_NTZ(bronze_data:_INGESTED_AT_UTC::VARCHAR) AS ingested_at_utc

    FROM source

),

coordinates_fixed AS (

    SELECT

        *,

        COALESCE(
            raw_latitude,
            report_location:coordinates[1]::FLOAT
        ) AS latitude,

        COALESCE(
            raw_longitude,
            report_location:coordinates[0]::FLOAT
        ) AS longitude

    FROM renamed

),

final AS (

    SELECT

        incident_number,
        incident_timestamp,

        EXTRACT(YEAR FROM incident_timestamp) AS incident_year,
        EXTRACT(MONTH FROM incident_timestamp) AS incident_month,
        EXTRACT(DAY FROM incident_timestamp) AS incident_day,
        EXTRACT(HOUR FROM incident_timestamp) AS incident_hour,

        incident_type,
        address,

        latitude,
        longitude,

        CASE
            WHEN latitude IS NOT NULL
             AND longitude IS NOT NULL
            THEN ST_POINT(longitude, latitude)
        END AS incident_geography,

        ingested_at_utc

    FROM coordinates_fixed

)

SELECT *
FROM final
WHERE incident_timestamp IS NOT NULL