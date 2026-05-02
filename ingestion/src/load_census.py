import requests
import polars as pl
import os
from dotenv import load_dotenv
from datetime import datetime
import geopandas as gpd
import zipfile
import io

load_dotenv()

START_YEAR = 2010
END_YEAR = datetime.now().year
BASE_URL = os.getenv("CENSUS_BASE_URL")
TRACTS_URL = os.getenv("CENSUS_TRACTS_URL")

def get_census_data() -> pl.DataFrame:

    yearly_df = []

    for year in range(START_YEAR, END_YEAR + 1):
        print(f"Fetching Census ACS data for {year}")

        try:
            url = f"{BASE_URL}/{year}/acs/acs5"
            params = {
                "get": "B01003_001E,B19013_001E",
                "for": "tract:*",
                "in": "state:53 county:033"  # Washington, King County
            }

            resp = requests.get(url, params=params)
            resp.raise_for_status()

            data = resp.json()

            census = pl.DataFrame(data[1:], schema=data[0]).with_columns([
                pl.lit(year).alias("year"),
                (pl.col("state") + pl.col("county") + pl.col("tract")).alias("geoid")
            ])

            yearly_df.append(census)

        except Exception as e:
            print(f"Failed for {year}: {e}")

    if not yearly_df:
        raise ValueError("No census data loaded")
    
    complete_census_data = pl.concat(yearly_df)

    return complete_census_data

def get_census_tiger_tracts() -> gpd.GeoDataFrame:
    url = TRACTS_URL

    print("Downloading TIGER shapefile...")

    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        extract_path = "tiger_tracts"
        os.makedirs(extract_path, exist_ok=True)
        z.extractall(extract_path)

    print("Reading shapefile...")

    tiger_shapefile = gpd.read_file(extract_path)

    return tiger_shapefile