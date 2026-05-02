import polars as pl
from datetime import datetime
import os
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