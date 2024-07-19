from pyspark.sql import SparkSession
from datetime import datetime, date
from pyspark.sql import Row
import os

SPARK_CONNECT_SERVER = os.getenv("SPARK_CONNECT_SERVER", "sc://172.25.0.2:30052")
spark = SparkSession.builder.remote(SPARK_CONNECT_SERVER).getOrCreate()

df = spark.createDataFrame(
    [
        Row(a=1, b=2.0, c="string1", d=date(2000, 1, 1), e=datetime(2000, 1, 1, 12, 0)),
        Row(a=2, b=3.0, c="string2", d=date(2000, 2, 1), e=datetime(2000, 1, 2, 12, 0)),
        Row(a=4, b=5.0, c="string3", d=date(2000, 3, 1), e=datetime(2000, 1, 3, 12, 0)),
    ]
)
df.show()

create_schema_df = spark.sql("CREATE DATABASE IF NOT EXISTS raw ")

df.writeTo("raw.demo").tableProperty(
    "write.format.default", "parquet"
).createOrReplace()
