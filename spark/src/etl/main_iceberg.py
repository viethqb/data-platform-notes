import os
from utils import get_spark

spark, logger = get_spark(job_name="main_spark")

DATA_PATH = os.getenv("DATA_PATH", "s3a://lakehouse/raw/yellow_tripdata/")
df = spark.read.option("mergeSchema", "true").parquet(DATA_PATH)

create_schema_df = spark.sql("CREATE DATABASE IF NOT EXISTS raw ")
create_schema_df.show()
# Create Iceberg table "nyc.taxis_large" from RDD
# df.write.mode("overwrite").saveAsTable("raw.taxis_spark")
df.writeTo("raw.taxis_spark").tableProperty(
    "write.format.default", "parquet"
).partitionedBy("y", "m").createOrReplace()
# Query table row count
count_df = spark.sql("SELECT COUNT(*) AS cnt FROM raw.taxis_spark")
total_rows_count = count_df.first().cnt
logger.info(f"Total Rows for NYC Taxi Data: {total_rows_count}")
