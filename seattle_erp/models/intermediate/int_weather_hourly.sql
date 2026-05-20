WITH deduplicated AS (

    SELECT *

    FROM {{ ref('slv_weather') }}

    QUALIFY ROW_NUMBER() OVER (

        PARTITION BY
            station_id,
            DATE_TRUNC('hour', observed_at_utc)

        ORDER BY observed_minute DESC

    ) = 1

)

SELECT *
FROM deduplicated
