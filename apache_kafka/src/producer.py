import logging
import pandas as pd
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)

producer = KafkaProducer(bootstrap_servers="192.168.221.215:30664")


total_processed = 0
i = 1
df = pd.read_parquet("./yellow_tripdata.csv")

count = 0
for index, row in df.sample(n=1000).iterrows():
    producer.send("my-topic", bytes(row.to_json(), "utf-8"))
    count += 1
producer.flush()
total_processed += count
if total_processed % 10000 * i == 0:
    logging.info(f"total processed till now {total_processed}")
    i += 1
