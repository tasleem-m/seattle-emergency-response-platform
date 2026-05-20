SELECT

    DATE_TRUNC('day', incident_timestamp) AS incident_date,

    COUNT(*) AS total_incidents,

    ROUND(AVG(temperature_f), 1) AS avg_temperature_f,

    ROUND(AVG(relative_humidity_pct), 1) AS avg_relative_humidity_pct,

    ROUND(AVG(wind_speed_mps), 2) AS avg_wind_speed_mps,

    ROUND(AVG(visibility_km), 2) AS avg_visibility_km,

    ROUND(SUM(precipitation_6hr_mm), 2) AS total_precipitation_mm,

    MODE(present_weather) AS dominant_weather_condition,

    MODE(incident_type) AS most_common_incident_type

FROM {{ ref('gld_incident_enriched') }}

GROUP BY 1
