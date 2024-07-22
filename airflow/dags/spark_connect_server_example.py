from __future__ import print_function
from builtins import range
from airflow.operators.empty import EmptyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import DAG
from pyspark.sql import SparkSession
from datetime import datetime, date, timedelta
from pyspark.sql import Row
import os
import time
from pprint import pprint

seven_days_ago = datetime.combine(datetime.today() - timedelta(7), datetime.min.time())

args = {
    "owner": "airflow",
    "start_date": seven_days_ago,
}

dag = DAG(dag_id="example_python_operator", default_args=args, schedule_interval=None)


def spark_connect_server_example():
    SPARK_CONNECT_SERVER = (
        "sc://sparglim-server-service.sparglim.svc.cluster.local:15002"
    )
    spark = SparkSession.builder.remote(SPARK_CONNECT_SERVER).getOrCreate()

    df = spark.createDataFrame(
        [
            Row(
                a=1,
                b=2.0,
                c="string1",
                d=date(2000, 1, 1),
                e=datetime(2000, 1, 1, 12, 0),
            ),
            Row(
                a=2,
                b=3.0,
                c="string2",
                d=date(2000, 2, 1),
                e=datetime(2000, 1, 2, 12, 0),
            ),
            Row(
                a=4,
                b=5.0,
                c="string3",
                d=date(2000, 3, 1),
                e=datetime(2000, 1, 3, 12, 0),
            ),
        ]
    )
    df.show()

    create_schema_df = spark.sql("CREATE DATABASE IF NOT EXISTS raw ")

    df.writeTo("raw.demo").tableProperty(
        "write.format.default", "parquet"
    ).createOrReplace()


start = EmptyOperator(
    task_id="start",
    dag=dag,
)

end = EmptyOperator(
    task_id="end",
    dag=dag,
)

spark_connect_server_example = PythonOperator(
    task_id="spark_connect_server_example",
    provide_context=True,
    python_callable=spark_connect_server_example,
    dag=dag,
)
start >> spark_connect_server_example >> end
