from sodapy import Socrata
import polars as pl
import os
import boto3
from datetime import datetime, timezone
from dotenv import load_dotenv

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
            print("No more data — finished ingestion.")
            break

        call_data = pl.from_dicts(results)
        print(f"Rows in df: {call_data.height}")

        if call_data.height == 0:
            print(f"Empty dataframe at offset={offset} — skipping.")
            offset += limit
            continue

        call_data = call_data.rename({col: col.upper() for col in call_data.columns})
        call_data = call_data.with_columns(
            pl.lit(datetime.now(timezone.utc)).alias("_INGESTED_AT_UTC")
        )

        print(f"Processing {len(call_data)} rows (offset={offset})")
        
        yield call_data

        offset += limit

def write_batch_to_s3(df):
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    creds = session.get_credentials().get_frozen_credentials()
    now = datetime.now(timezone.utc)

    path = (
        f"{BASE_PATH}/911_calls/"
        f"year={now.year}/month={now.month:02}/day={now.day:02}/"
        f"calls_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
    )

    df.write_parquet(
        path,
        storage_options={
            "aws_access_key_id": creds.access_key,
            "aws_secret_access_key": creds.secret_key,
            "aws_session_token": creds.token,
            "region": REGION,
        }
    )

    print(f"Wrote batch to {path}")