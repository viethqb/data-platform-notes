import logging
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession
from config import *


def load_config(spark_context: SparkContext):
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.access.key", AWS_ACCESS_KEY_ID)
    spark_context._jsc.hadoopConfiguration().set(
        "fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY
    )
    spark_context._jsc.hadoopConfiguration().set("fs.s3a.endpoint", S3_ENDPOINT)
    spark_context._jsc.hadoopConfiguration().set(
        "fs.s3a.connection.ssl.enabled", S3_SSL_ENABLE
    )
    spark_context._jsc.hadoopConfiguration().set(
        "fs.s3a.path.style.access", S3_PATH_STYLE_ACCESS
    )
    spark_context._jsc.hadoopConfiguration().set(
        "fs.s3a.attempts.maximum", S3_ATTEMPTS_MAXIMUM
    )
    spark_context._jsc.hadoopConfiguration().set(
        "fs.s3a.connection.establish.timeout", S3_CONNECTION_ESTABLISH_TIMEOUT
    )
    spark_context._jsc.hadoopConfiguration().set(
        "fs.s3a.connection.timeout", S3_CONNECTION_TIMEOUT
    )


def get_spark(
    job_name,
):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(job_name)

    # adding iceberg configs
    conf = (
        SparkConf()
        .set(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )  # Use Iceberg with Spark
        .set("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog")
        .set(
            "spark.sql.catalog.lakehouse.io-impl", "org.apache.iceberg.aws.s3.S3FileIO"
        )
        .set("spark.sql.catalog.lakehouse.warehouse", S3_WAREHOUSE)
        .set("spark.sql.catalog.lakehouse.s3.path-style-access", S3_PATH_STYLE_ACCESS)
        .set(
            "spark.sql.catalog.lakehouse.s3.endpoint",
            S3_HTTP_ENDPOINT,
        )
        .set("spark.sql.defaultCatalog", "lakehouse")  # Name of the Iceberg catalog
        .set("spark.sql.catalogImplementation", "in-memory")
        .set("spark.sql.catalog.lakehouse.type", "hive")  # Iceberg catalog type
        .set("spark.sql.catalog.lakehouse.uri", METASTORE_URI)
        .set("spark.executor.heartbeatInterval", "300000")
        .set("spark.network.timeout", "400000")
    )

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    # Disable below line to see INFO logs
    spark.sparkContext.setLogLevel("ERROR")
    load_config(spark.sparkContext)

    return spark, logger
