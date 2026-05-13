WITH monthly_aggregated AS (

    SELECT

        DATE_TRUNC('month', incident_timestamp) AS incident_month,

        incident_type,

        COUNT(*) AS total_incidents,

        COUNT(DISTINCT DATE_TRUNC('day', incident_timestamp))
            AS active_incident_days,

        ROUND(
            COUNT(*)::FLOAT
            / NULLIF(
                COUNT(DISTINCT DATE_TRUNC('day', incident_timestamp)),
                0
            ),
            2
        ) AS avg_daily_incidents

    FROM {{ ref('gld_incident_enriched') }}

    GROUP BY 1, 2

),

final AS (

    SELECT

        *,

        ROUND(
            AVG(total_incidents) OVER (

                PARTITION BY incident_type
                ORDER BY incident_month

                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW

            ),
            2
        ) AS rolling_3_month_avg_incidents

    FROM monthly_aggregated

)

SELECT *
FROM final