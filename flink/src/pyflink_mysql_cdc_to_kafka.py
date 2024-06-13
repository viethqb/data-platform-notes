import logging
import sys
import os

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment


def pyflink_mysql_cdc_to_kafka():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    t_env = StreamTableEnvironment.create(stream_execution_environment=env)

    t_env.execute_sql(
        """
    CREATE TABLE IF NOT EXISTS customers_mysql_cdc_src(
        `id` BIGINT NOT NULL,
        `first_name` STRING NOT NULL,
        `last_name` STRING NOT NULL,
        `email` STRING NOT NULL,
        PRIMARY KEY(`id`) NOT ENFORCED
    ) with (
        'connector' = 'mysql-cdc',
        'hostname' = 'mysql.data-source',
        'port' = '3306',
        'username' = 'root',
        'password' = 'debezium',
        'database-name' = 'inventory',
        'table-name' = 'customers'
    );"""
    )

    t_env.execute_sql(
        """
    create table customers_iceberg WITH (
        'connector' = 'iceberg', 
        'catalog-name' = 'iceberg_catalog', 
        'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO', 
        'client.assume-role.region' = 'us-east-1', 
        'catalog-type' = 'hive', 'uri' = 'thrift://hive-metastore.metastore.svc.cluster.local:9083', 
        'warehouse' = 's3://lakehouse', 
        's3.endpoint' = 'http://minio.minio.svc.cluster.local:9000', 
        's3.path-style-access' = 'true', 
        's3.access.key' = 'admin', 
        's3.secret.key' = 'password', 
        'format-version' = '2'
    ) LIKE customers_mysql_cdc_src (EXCLUDING OPTIONS);
    """
    )

    t_env.execute_sql(
        "INSERT INTO customers_iceberg SELECT * FROM customers_mysql_cdc_src"
    )


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    pyflink_mysql_cdc_to_kafka()
