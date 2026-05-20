from utils.snowflake_helper import get_connection

COPY_COMMANDS = [

    """
    COPY INTO bronze.brz_911_calls
    FROM @capstone.intermediate.bronze_stage/911_calls/
    FILE_FORMAT = (TYPE = PARQUET);
    """,

    """
    COPY INTO bronze.brz_weather
    FROM @capstone.intermediate.bronze_stage/weather/
    FILE_FORMAT = (TYPE = PARQUET);
    """,

    """
    COPY INTO bronze.brz_census
    FROM @capstone.intermediate.bronze_stage/census/
    FILE_FORMAT = (TYPE = PARQUET);
    """
]


def load_to_snowflake():

    conn = get_connection()

    try:
        cursor = conn.cursor()

        for command in COPY_COMMANDS:

            cursor.execute(command)

            results = cursor.fetchall()

            print(results)

    finally:
        cursor.close()
        conn.close()
