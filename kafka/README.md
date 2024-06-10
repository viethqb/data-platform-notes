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
k apply -f deployment/kafka/sink-my-topic-to-s3-connector.yaml
```
### Debeziums mysql test
```bash
# start mysql source
k apply -f deployment/kafka/namespace.yaml
k apply -f deployment/kafka/deployment.yaml
k apply -f deployment/kafka/serrvice.yaml

# mysql cdc source connector
k apply -f deployment/kafka/debezium-connector-mysql.yaml
# update data source
k run mysql-client --image=mysql:5.7 -it --rm --restart=Never --namespace=kafka -- /bin/bash
bash-4.2# mysql -uroot -P3306 -hmysql.data-source -p
mysql> use inventory;
mysql> update customers set first_name="Sally Marie" where id=1001;
# Query OK, 1 row affected (0.27 sec)
# Rows matched: 1  Changed: 1  Warnings: 0

#check 
k -n kafka exec -it my-kafka-cluster-kafka-0 bash
[kafka@my-kafka-cluster-kafka-0 kafka]$ bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic customers --from-beginning
#{"before":null,"after":{"id":1001,"first_name":"Sally Marie 1","last_name":"Thomas","email":"sally.thomas@acme.com"},"source":{"version":"2.4.2.Final","connector":"mysql","name":"mysql","ts_ms":1717999936000,"snapshot":"first_in_data_collection","db":"inventory","sequence":null,"table":"customers","server_id":0,"gtid":null,"file":"mysql-bin.000003","pos":953,"row":0,"thread":null,"query":null},"op":"r","ts_ms":1717999936070,"transaction":null}
#{"before":null,"after":{"id":1002,"first_name":"George","last_name":"Bailey","email":"gbailey@foobar.com"},"source":{"version":"2.4.2.Final","connector":"mysql","name":"mysql","ts_ms":1717999936000,"snapshot":"true","db":"inventory","sequence":null,"table":"customers","server_id":0,"gtid":null,"file":"mysql-bin.000003","pos":953,"row":0,"thread":null,"query":null},"op":"r","ts_ms":1717999936070,"transaction":null}
#{"before":null,"after":{"id":1003,"first_name":"Edward","last_name":"Walker","email":"ed@walker.com"},"source":{"version":"2.4.2.Final","connector":"mysql","name":"mysql","ts_ms":1717999936000,"snapshot":"true","db":"inventory","sequence":null,"table":"customers","server_id":0,"gtid":null,"file":"mysql-bin.000003","pos":953,"row":0,"thread":null,"query":null},"op":"r","ts_ms":1717999936070,"transaction":null}
#{"before":null,"after":{"id":1004,"first_name":"Anne","last_name":"Kretchmar","email":"annek@noanswer.org"},"source":{"version":"2.4.2.Final","connector":"mysql","name":"mysql","ts_ms":1717999936000,"snapshot":"last_in_data_collection","db":"inventory","sequence":null,"table":"customers","server_id":0,"gtid":null,"file":"mysql-bin.000003","pos":953,"row":0,"thread":null,"query":null},"op":"r","ts_ms":1717999936070,"transaction":null}
#{"before":{"id":1001,"first_name":"Sally Marie 1","last_name":"Thomas","email":"sally.thomas@acme.com"},"after":{"id":1001,"first_name":"Sally Marie","last_name":"Thomas","email":"sally.thomas@acme.com"},"source":{"version":"2.4.2.Final","connector":"mysql","name":"mysql","ts_ms":1718001145000,"snapshot":"false","db":"inventory","sequence":null,"table":"customers","server_id":223344,"gtid":null,"file":"mysql-bin.000003","pos":1197,"row":0,"thread":34,"query":null},"op":"u","ts_ms":1718001145612,"transaction":null}

k apply -f deployment/kafka/sink-mysql-kafka-topic-to-s3-connector.yaml
```

### Debeziums postgres test

```bash
# Create postgres DB
k apply -f deployment/postgres/postgres.yaml

# Create debezium cdc source connector
k apply -f deployment/kafka/debezium-connector-postgres.yaml
k apply -f deployment/postgres/postgresql-client.yml
k -n kafka exec -it postgresql-client sh
data_engineer=# \dt inventory.*
#                   List of relations
#   Schema   |       Name       | Type  |     Owner     
# -----------+------------------+-------+---------------
#  inventory | customers        | table | data_engineer
#  inventory | geom             | table | data_engineer
#  inventory | orders           | table | data_engineer
#  inventory | products         | table | data_engineer
#  inventory | products_on_hand | table | data_engineer
#  inventory | spatial_ref_sys  | table | data_engineer
# (6 rows)
update inventory.customers set first_name='Sally Marie' where id=1001;
k apply  -f deployment/kafka/sink-postgres-kafka-topic-to-s3-connector.yaml
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


CREATE TABLE IF NOT EXISTS minio.raw.customers(
	json_string             varchar,
    year                    varchar,
    month                   varchar,
    day                     varchar,
    hour                    varchar
)WITH
(
 	format = 'TEXTFILE',
 	partitioned_by = ARRAY[ 'year', 'month', 'day', 'hour' ],
 	external_location = 's3a://kafka/topics/customers'
);
trino> CALL minio.system.sync_partition_metadata('raw', 'customers', 'FULL');
trino> select * from minio.raw.customers;
```
## Destroy kind

```bash
kind delete cluster -n dev 
```