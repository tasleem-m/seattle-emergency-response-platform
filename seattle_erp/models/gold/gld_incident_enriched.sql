WITH incident_tracts AS (

    SELECT

        i.*,

        t.tract_geoid,
        t.tract_name,
        t.tract_full_name

    FROM {{ ref('slv_911_calls') }} i

    LEFT JOIN {{ ref('slv_census_tracts') }} t
        ON ST_CONTAINS(
            t.tract_geography,
            i.incident_geography
        )

),

incident_demographics AS (

    SELECT

        it.*,

        d.census_year,
        d.total_population,
        d.median_household_income

    FROM incident_tracts it

    LEFT JOIN {{ ref('slv_census') }} d
        ON it.tract_geoid = d.tract_geoid
        AND it.incident_year = d.census_year

),

incident_weather AS (

    SELECT

        id.*,

        w.temperature_c,
        ROUND((w.temperature_c * 9/5) + 32, 1) AS temperature_f,

        w.relative_humidity_pct,
        w.wind_speed_mps,
        w.precipitation_6hr_mm,
        w.visibility_km,

        w.present_weather

    FROM incident_demographics id

    LEFT JOIN {{ ref('int_weather_hourly') }} w
        ON DATE_TRUNC('hour', id.incident_timestamp)
         = DATE_TRUNC('hour', w.observed_at_utc)

)

SELECT *
FROM incident_weather