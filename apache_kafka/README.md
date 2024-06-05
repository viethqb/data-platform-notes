## Create k8s cluster (kind)
```bash
kind create cluster --name dev --config deployment/kind/kind-config.yaml
kubectl get no -owide
# NAME                STATUS   ROLES           AGE    VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION     CONTAINER-RUNTIME
# dev-control-plane   Ready    control-plane   153m   v1.27.3   172.25.0.5    <none>        Debian GNU/Linux 11 (bullseye)   6.5.0-35-generic   containerd://1.7.1
# dev-worker          Ready    <none>          152m   v1.27.3   172.25.0.4    <none>        Debian GNU/Linux 11 (bullseye)   6.5.0-35-generic   containerd://1.7.1
# dev-worker2         Ready    <none>          152m   v1.27.3   172.25.0.3    <none>        Debian GNU/Linux 11 (bullseye)   6.5.0-35-generic   containerd://1.7.1
# dev-worker3         Ready    <none>          152m   v1.27.3   172.25.0.2    <none>        Debian GNU/Linux 11 (bullseye)   6.5.0-35-generic   containerd://1.7.1
```
## Nginx ingress
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --set controller.hostNetwork=true,controller.service.type="",controller.kind=DaemonSet --namespace ingress-nginx --version 4.10.1 --create-namespace --debug

kubectl -n ingress-nginx get po -owide
```
## Install Minio on Kubernetes

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm upgrade --install minio -n minio -f deployment/minio/minio-values.yaml bitnami/minio --create-namespace --debug --version 14.6.0
kubectl -n minio get po
```
## Install Hive Metastore

### hive-metastore-postgresql
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm upgrade --install metastore-db -n metastore -f deployment/hive/hive-metastore-postgres-values.yaml bitnami/postgresql --create-namespace --debug --version 15.4.2
```
### Hive metastore
```bash
# docker pull rtdl/hive-metastore:3.1.2
# kind load docker-image rtdl/hive-metastore:3.1.2 --name dev
helm upgrade --install hive-metastore -n metastore -f deployment/hive/hive-metastore-values.yaml ../charts/hive-metastore --create-namespace --debug
```
## Install Trino
```bash
helm repo add trino https://trinodb.github.io/charts
helm upgrade --install trino -n trino -f deployment/trino/trino-values.yaml trino/trino --create-namespace --debug --version 0.21.0

kubectl -n trino get po
```

## Install Kafka

### Install Strimzi Operator

```bash
helm repo add strimzi https://strimzi.io/charts/
helm install kafka-operator strimzi/strimzi-kafka-operator --namespace=kafka --create-namespace --debug --version 0.41.0
```

### Create Kafka Cluster

```bash
kubectl apply -f deployment/kafka/kafka-cluster.yaml
```
### Create Kafka topic

```bash
kubectl apply -f deployment/kafka/connect-configs-topic.yaml
kubectl apply -f deployment/kafka/connect-offsets-topic.yaml
kubectl apply -f deployment/kafka/connect-status-topic.yaml
kubectl apply -f deployment/kafka/my-topic-topic.yaml
kubectl -n kafka exec -it my-kafka-cluster-kafka-0 bash
[kafka@my-kafka-cluster-kafka-0 kafka]$ bin/kafka-topics.sh --list --bootstrap-server localhost:9092
# connect-configs
# connect-offsets
# connect-status
# my-topic
[kafka@my-kafka-cluster-kafka-0 kafka]$ bin/kafka-topics.sh --list --bootstrap-server 172.25.0.2:32100,172.25.0.3:32100,172.25.0.4:32100 
# 172.25.0.2,172.25.0.3,172.25.0.4 is node ip
# connect-configs
# connect-offsets
# connect-status
# my-topic
```
### Produce message to my-topic

```bash
python3 --version         
# Python 3.10.12
pip install -r src/requirements.txt
python3 src/producer.py
bin/kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server 172.25.0.2:32100,172.25.0.3:32100,172.25.0.4:32100
```
### Build kafka connect image

```bash
# Replace viet1846 by your repository
docker build -t viet1846/kafka-connect:0.41.0 -f deployment/kafka/Dockerfile deployment/kafka 
docker push viet1846/kafka-connect:0.41.0
```

### Create kafka connect and Kafka connector
```bash
k apply -f deployment/kafka/connect.yaml
k apply -f deployment/kafka/connector.yaml
```

### Query data by Trino
```bash
trino> CREATE SCHEMA lakehouse.raw WITH (location = 's3a://lakehouse/raw/');

trino> CREATE TABLE IF NOT EXISTS minio.raw.mytopic(
	DOLocationID            bigint,
	RatecodeID              bigint,
	fare_amount             double,
	tpep_dropoff_datetime   varchar,
	congestion_surcharge    double,
	VendorID                bigint,
	passenger_count         bigint,
	tolls_amount            bigint,
	Airport_fee             bigint,
	improvement_surcharge   bigint,
	messageTS               varchar,
	trip_distance           double,
	store_and_fwd_flag      varchar,
	payment_type            bigint,
	total_amount            double,
	extra                   bigint,
	tip_amount              double,
	mta_tax                 double,
	tpep_pickup_datetime    varchar,
	PULocationID            bigint,
    year                    varchar,
    month                   varchar,
    day                     varchar,
    hour                    varchar
)WITH
(
 	format = 'JSON',
 	partitioned_by = ARRAY[ 'year', 'month', 'day', 'hour' ],
 	external_location = 's3a://kafka/topics/my-topic'
);
trino> CALL minio.system.sync_partition_metadata('raw', 'mytopic', 'FULL');
trino> select * from minio.raw.mytopic;
trino> CREATE TABLE IF NOT EXISTS minio.raw.mytopic_textfile(
	json_string             varchar,
    year                    varchar,
    month                   varchar,
    day                     varchar,
    hour                    varchar
)WITH
(
 	format = 'TEXTFILE',
 	partitioned_by = ARRAY[ 'year', 'month', 'day', 'hour' ],
 	external_location = 's3a://kafka/topics/my-topic'
);
trino> CALL minio.system.sync_partition_metadata('raw', 'mytopic_textfile', 'FULL');
trino> select * from minio.raw.mytopic_textfile;
```
## Destroy kind

```bash
kind delete cluster -n dev 
```