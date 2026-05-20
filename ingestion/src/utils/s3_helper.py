import os
import tempfile
from datetime import UTC, datetime

import boto3
from dotenv import load_dotenv

load_dotenv()

BASE_PATH = os.getenv("S3_BASE_PATH")
PROFILE = os.getenv("AWS_PROFILE_NAME")
REGION = os.getenv("AWS_REGION")

def write_parquet_to_s3(df, file_name):
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    creds = session.get_credentials().get_frozen_credentials()
    now = datetime.now(UTC)

    path = (
        f"{BASE_PATH}/{file_name}/"
        f"year={now.year}/month={now.month:02}/day={now.day:02}/"
        f"{file_name}_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
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

    (f"Wrote to {path}")

def write_geo_parquet_to_s3(gdf, file_name):
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    s3 = session.client("s3")

    now = datetime.now(UTC)

    key = (
        f"{file_name}/"
        f"year={now.year}/month={now.month:02}/day={now.day:02}/"
        f"{file_name}_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
    )

    bucket = BASE_PATH.replace("s3://", "").split("/")[0]
    prefix = "/".join(BASE_PATH.replace("s3://", "").split("/")[1:])
    full_key = f"{prefix}/{key}"

    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        tmp_path = tmp.name

    gdf.to_parquet(tmp_path, engine="pyarrow")

    (f"Uploading to s3://{bucket}/{full_key}")
    s3.upload_file(tmp_path, bucket, full_key)

    os.remove(tmp_path)

    (f"Wrote to s3://{bucket}/{full_key}")
