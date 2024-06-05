import logging
import time
import pandas as pd
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)

producer = KafkaProducer(bootstrap_servers="192.168.221.215:30664")


total_processed = 0
i = 1
df = pd.read_csv("./yellow_tripdata.csv")

while True:
    for index, row in df.sample(n=10).iterrows():
        producer.send("my-topic", bytes(row.to_json(), "utf-8"))
    producer.flush()
    time.sleep(1)
