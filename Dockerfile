FROM apache/airflow:2.9.3-python3.11

USER airflow

RUN pip install --no-cache-dir \
    dbt-snowflake \
    polars \
    sodapy \
    geopandas \