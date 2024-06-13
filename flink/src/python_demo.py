import logging
import sys
import os

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment


def pyflink_hello_world():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    t_env = StreamTableEnvironment.create(stream_execution_environment=env)

    t_env.execute_sql(
        """
    CREATE TABLE datagen(
        id    BIGINT,
        data  STRING
    ) WITH (
        'connector' = 'datagen',
        'rows-per-second' = '10'
    );"""
    )

    t_env.execute_sql(
        """
    CREATE TABLE datagen_sink (
     id    BIGINT,
     data  STRING
    ) WITH (
     'connector' = 'kafka',
     'topic' = 'datagen',
     'properties.bootstrap.servers' = 'my-kafka-cluster-kafka-plain-bootstrap.kafka.svc.cluster.local:9092',
     'properties.group.id' = 'datagen-sink',
     'format' = 'json'
    )
    """
    )

    t_env.execute_sql("INSERT INTO datagen_sink SELECT * FROM datagen")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    pyflink_hello_world()
