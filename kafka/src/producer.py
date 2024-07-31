from time import time
from kafka import KafkaProducer
from faker import Faker
import json, time
import os

BOOTSTRAP_SERVERS = os.getenv(
    "BOOTSTRAP_SERVERS", "172.25.0.2:32100,172.25.0.3:32100,172.25.0.4:32100"
)

producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)

faker = Faker()


def get_register():
    return {"name": faker.name(), "add": faker.year()}


def get_partitioner(key_bytes, all_partitions, available_partitions):
    return 0


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,  # server name
    value_serializer=json_serializer,  # function callable
    # partitioner = get_partitioner, # function return 0 >>> only partition_0 can received messages
)

while 1 == 1:
    user = get_register()
    # print(user)
    producer.send("users", user)
    time.sleep(1)
