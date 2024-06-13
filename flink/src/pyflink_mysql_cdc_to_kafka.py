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
    CREATE TABLE customers_kafka_sink (
        `id` BIGINT NOT NULL,
        `first_name` STRING NOT NULL,
        `last_name` STRING NOT NULL,
        `email` STRING NOT NULL,
        PRIMARY KEY(`id`) NOT ENFORCED
    ) WITH (
        'connector' = 'upsert-kafka',
        'topic' = 'customers-flink',
        'properties.bootstrap.servers' = 'my-kafka-cluster-kafka-plain-bootstrap.kafka.svc.cluster.local:9092',
        'properties.group.id' = 'customers-flink-sink',
        'key.format' = 'json',
        'key.fields-prefix' = 'key_',
        'value.format' = 'json',
        'value.fields-prefix' = 'value_',
        'value.fields-include' = 'EXCEPT_KEY'
    )
    """
    )

    t_env.execute_sql(
        "INSERT INTO customers_kafka_sink SELECT * FROM customers_mysql_cdc_src"
    )


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    pyflink_mysql_cdc_to_kafka()
