WITH source AS (

    SELECT
        $1 AS bronze_data
    FROM {{ source('BRONZE', 'BRZ_WEATHER') }}

),

renamed AS (

    SELECT

        -- station identifiers
        bronze_data:STATION::VARCHAR AS station_id,
        bronze_data:Station_name::VARCHAR AS station_name,

        -- timestamp
        TRY_TO_TIMESTAMP_NTZ(
            bronze_data:DATE::VARCHAR
        ) AS observed_at_utc,

        bronze_data:Year::INTEGER AS observed_year,
        bronze_data:Month::INTEGER AS observed_month,
        bronze_data:Day::INTEGER AS observed_day,
        bronze_data:Hour::INTEGER AS observed_hour,
        bronze_data:Minute::INTEGER AS observed_minute,

        -- station location
        bronze_data:LATITUDE::FLOAT AS latitude,
        bronze_data:LONGITUDE::FLOAT AS longitude,
        bronze_data:ELEVATION::FLOAT AS elevation_meters,

        -- temperatures
        bronze_data:temperature::FLOAT AS temperature_c,
        bronze_data:dew_point_temperature::FLOAT AS dew_point_c,
        bronze_data:wet_bulb_temperature::FLOAT AS wet_bulb_temperature_c,

        -- humidity
        bronze_data:relative_humidity::FLOAT AS relative_humidity_pct,

        -- pressure
        bronze_data:station_level_pressure::FLOAT AS station_pressure_hpa,
        bronze_data:sea_level_pressure::FLOAT AS sea_level_pressure_hpa,
        bronze_data:pressure_3hr_change::FLOAT AS pressure_3hr_change_hpa,

        -- wind
        bronze_data:wind_direction::FLOAT AS wind_direction_degrees,
        bronze_data:wind_speed::FLOAT AS wind_speed_mps,

        -- precipitation
        bronze_data:precipitation_6_hour::FLOAT AS precipitation_6hr_mm,

        -- visibility
        bronze_data:visibility::FLOAT AS visibility_km,

        -- weather conditions
        bronze_data:pres_wx_MW1::VARCHAR AS present_weather,

        -- remarks
        bronze_data:REM::VARCHAR AS weather_remark,

        -- quality codes
        bronze_data:temperature_Quality_Code::VARCHAR AS temperature_qc,
        bronze_data:wind_speed_Quality_Code::VARCHAR AS wind_speed_qc,
        bronze_data:visibility_Quality_Code::VARCHAR AS visibility_qc,

        -- report metadata
        bronze_data:temperature_Report_Type::VARCHAR AS report_type,

        ST_POINT(longitude, latitude) AS station_geography,

        -- ingestion metadata
        CURRENT_TIMESTAMP() AS transformed_at_utc

    FROM source
    WHERE TRY_TO_TIMESTAMP_NTZ(
            bronze_data:DATE::VARCHAR
        ) IS NOT NULL

)

SELECT *
FROM renamed