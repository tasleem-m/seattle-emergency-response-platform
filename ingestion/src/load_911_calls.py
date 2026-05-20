import os
from datetime import UTC, datetime

import polars as pl
from dotenv import load_dotenv
from sodapy import Socrata

load_dotenv()

TOKEN = os.environ["911_TOKEN"]
BASE_PATH = os.getenv("S3_BASE_PATH")
PROFILE = os.getenv("AWS_PROFILE_NAME")
REGION = os.getenv("AWS_REGION")

def get_911_call_data():

    client = Socrata("data.seattle.gov", TOKEN)

    limit = 5000
    offset = 0

    while True:
        results = client.get(
            "kzjm-xkqj",
            limit=limit,
            offset=offset,
            order="datetime ASC"
            )

        if not results:
            break

        call_data = pl.from_dicts(results)
        (f"Rows in df: {call_data.height}")

        if call_data.height == 0:
            (f"Empty dataframe at offset={offset} — skipping.")
            offset += limit
            continue

        call_data = call_data.rename({col: col.upper() for col in call_data.columns})
        call_data = call_data.with_columns(
            pl.lit(datetime.now(UTC)).alias("_INGESTED_AT_UTC")
        )

        (f"Processing {len(call_data)} rows (offset={offset})")

        yield call_data

        offset += limit
