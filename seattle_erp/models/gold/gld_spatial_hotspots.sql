SELECT
    census_year,
    
    tract_geoid,

    tract_name,
    tract_full_name,

    total_population,
    median_household_income,

    COUNT(*) AS total_incidents,

    ROUND(
        COUNT(*) / NULLIF(total_population, 0) * 1000,
        2
    ) AS incidents_per_1000_residents,

    ROUND(AVG(temperature_f), 1) AS avg_temperature_f,

    ROUND(AVG(precipitation_6hr_mm), 2) AS avg_precipitation_mm,

    MODE(incident_type) AS most_common_incident_type

FROM {{ ref('gld_incident_enriched') }}

WHERE tract_geoid IS NOT NULL AND census_year IS NOT NULL

GROUP BY

    census_year,
    tract_geoid,
    tract_name,
    tract_full_name,
    total_population,
    median_household_income
