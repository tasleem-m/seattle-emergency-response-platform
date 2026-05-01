import polars as pl
from datetime import datetime, timezone
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

BASE_PATH = os.getenv("S3_BASE_PATH")
PROFILE = os.getenv("AWS_PROFILE_NAME")
REGION = os.getenv("AWS_REGION")

STATION_ID = os.getenv("WEATHER_STATION_ID")
START_YEAR = 2010
END_YEAR = datetime.now().year
BASE_URL = os.getenv("WEATHER_BASE_URL")


def get_weather_data() -> pl.DataFrame:
    yearly_df = []

    for year in range(START_YEAR, END_YEAR + 1):
        url = f"{BASE_URL}/{year}/parquet/GHCNh_{STATION_ID}_{year}.parquet"
        
        print(f"Scanning: {url}")
        
        try:
            weather = pl.scan_parquet(url)

            yearly_df.append(weather)

        except Exception as e:
            print(f"Failed for {year}: {e}")

    if not yearly_df:
        raise ValueError("No weather data could be loaded.")

    complete_weather_data = (
        pl.concat(yearly_df)
        .collect()
    )

    return complete_weather_data

def write_parquet_to_s3(df):
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    creds = session.get_credentials().get_frozen_credentials()
    now = datetime.now(timezone.utc)

    path = (
        f"{BASE_PATH}/weather/"
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