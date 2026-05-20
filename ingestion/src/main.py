from load_911_calls import get_911_call_data
from load_weather import get_weather_data
from load_census import get_census_data, get_census_tiger_tracts
from utils.s3_helper import write_parquet_to_s3 as w, write_geo_parquet_to_s3 as wg
from load_raw_to_snowflake import load_to_snowflake

def main():
    for batch in get_911_call_data():
        w(batch, "911_calls")

    w(get_weather_data(), "weather")

    w(get_census_data(), "census")
    wg(get_census_tiger_tracts(), "census_tracts")

    load_to_snowflake()

if __name__ == "__main__":
    main()
