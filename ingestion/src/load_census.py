import io
import os
import time
import zipfile
from datetime import datetime

import geopandas as gpd
import polars as pl
import requests
from dotenv import load_dotenv

load_dotenv()

START_YEAR = 2010
END_YEAR = datetime.now().year
BASE_URL = os.getenv("CENSUS_BASE_URL")
TRACTS_URL = os.getenv("CENSUS_TRACTS_URL")
API_KEY = os.getenv("CENSUS_API_KEY")

def get_census_data() -> pl.DataFrame:

    yearly_df = []

    for year in range(START_YEAR, END_YEAR + 1):
        (f"Fetching Census ACS data for {year}")

        try:
            url = f"{BASE_URL}/{year}/acs/acs5"
            params = {
                "get": "B01003_001E,B19013_001E",
                "for": "tract:*",
                "in": "state:53 county:033",  # Washington, King County
                "key": API_KEY
            }

            resp = requests.get(url, params=params, timeout=30)
            (f"Status code for {year}: {resp.status_code}")

            resp.raise_for_status()

            try:
                data = resp.json()

            except Exception:
                (f"Invalid JSON response for {year}")
                (resp.text[:500])
                continue

            if len(data) <= 1:
                (f"No data returned for {year}")
                continue

            census = pl.DataFrame(data[1:], schema=data[0]).with_columns([
                pl.lit(year).alias("year"),
                (pl.col("state") + pl.col("county") + pl.col("tract")).alias("geoid")
            ])

            yearly_df.append(census)
            (f"Successfully loaded Census data for {year}")

            time.sleep(1)

        except Exception as e:
            (f"Failed for {year}: {e}")

    if not yearly_df:
        raise ValueError("No census data loaded")

    complete_census_data = pl.concat(yearly_df)

    return complete_census_data

def get_census_tiger_tracts() -> gpd.GeoDataFrame:
    url = TRACTS_URL

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        extract_path = "tiger_tracts"
        os.makedirs(extract_path, exist_ok=True)
        z.extractall(extract_path)

    tiger_shapefile = gpd.read_file(extract_path)

    for col in tiger_shapefile.columns:
        if col != "geometry":
            tiger_shapefile[col] = tiger_shapefile[col].astype(str)

    tiger_shapefile["geometry"] = tiger_shapefile["geometry"].to_wkt()

    return tiger_shapefile
