from load_911_calls import get_911_call_data, write_batch_to_s3

def main():
    for batch in get_911_call_data():
        write_batch_to_s3(batch)

if __name__ == "__main__":
    main()
