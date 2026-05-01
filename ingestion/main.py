from load_911_calls import get_911_call_data, write_batch_to_s3
from load_weather import get_weather_data, write_parquet_to_s3

def main():
    for batch in get_911_call_data():
        write_batch_to_s3(batch)
    
    write_parquet_to_s3(get_weather_data())

if __name__ == "__main__":
    main()
