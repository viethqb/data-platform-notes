import logging
import time
import pandas as pd
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)

producer = KafkaProducer(
    bootstrap_servers="172.25.0.2:32100,172.25.0.3:32100,172.25.0.4:32100"
)


total_processed = 0
i = 1
df = pd.read_csv("./src/yellow_tripdata.csv")

while True:
    for index, row in df.sample(n=1000).iterrows():
        producer.send("my-topic", bytes(row.to_json(), "utf-8"))
    producer.flush()
    time.sleep(1)
