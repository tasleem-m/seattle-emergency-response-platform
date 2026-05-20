WITH aggregated AS (

    SELECT

        census_year,

        tract_geoid,

        tract_name,
        tract_full_name,

        total_population,

        median_household_income,

        COUNT(*) AS total_incidents,

        ROUND(
            COUNT(*)::FLOAT
            / NULLIF(total_population, 0)
            * 1000,
            2
        ) AS incidents_per_1000_residents

    FROM {{ ref('gld_incident_enriched') }}

    WHERE
        tract_geoid IS NOT NULL
        AND total_population IS NOT NULL

    GROUP BY

        census_year,

        tract_geoid,

        tract_name,
        tract_full_name,

        total_population,
        median_household_income

),

ranked AS (

    SELECT

        *,

        DENSE_RANK() OVER (
            PARTITION BY census_year
            ORDER BY incidents_per_1000_residents DESC
        ) AS incident_burden_rank,

        NTILE(5) OVER (
            PARTITION BY census_year
            ORDER BY incidents_per_1000_residents DESC
        ) AS incident_burden_quintile

    FROM aggregated

)

SELECT *
FROM ranked
