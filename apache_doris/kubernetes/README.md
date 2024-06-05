## Note
```text
source: https://github.com/IvanWoo/trino-on-kubernetes
```

## Create k8s cluster (kind)
```bash
kind create cluster --name dev --config deployment/kind/kind-config.yaml 
```
## Nginx ingress
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --set controller.hostNetwork=true,controller.service.type="",controller.kind=DaemonSet --namespace ingress-nginx --version 4.10.1 --create-namespace --debug

k -n ingress-nginx get po -owide
```
## Install Minio on Kubernetes

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm upgrade --install minio -n minio -f deployment/minio/minio-values.yaml bitnami/minio --create-namespace --debug --version 14.6.0

kubectl -n minio get svc                                
# NAME    TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
# minio   ClusterIP   10.96.79.179   <none>        9000/TCP,9001/TCP   3h13m

kubectl get no -owide
# NAME                STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION     CONTAINER-RUNTIME
# dev-control-plane   Ready    control-plane   22m   v1.30.0   172.25.0.2    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15
# dev-worker          Ready    <none>          21m   v1.30.0   172.25.0.4    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15
# dev-worker2         Ready    <none>          21m   v1.30.0   172.25.0.3    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15
# dev-worker3         Ready    <none>          21m   v1.30.0   172.25.0.5    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15

# Add the following lines to the end of the /etc/hosts
# 172.25.0.4  minio.lakehouse.local
# init data test
# k run minio-client --image=minio/minio -it --rm --restart=Never --command /bin/bash
# mc alias set minio http://minio.minio.svc.cluster.local:9000 admin password 
# curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2009-01.parquet -o yellow_tripdata_2009-01.parquet
# mc cp ./yellow_tripdata_2009-01.parquet minio/lakehouse/raw/yellow_tripdata/y=2009/m=01/yellow_tripdata_2009-01.parquet
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

kubectl -n metastore get svc         
# NAME                         TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
# hive-metastore               ClusterIP   10.96.46.36   <none>        9083/TCP   179m
# metastore-db-postgresql      ClusterIP   10.96.71.7    <none>        5432/TCP   3h12m
# metastore-db-postgresql-hl   ClusterIP   None          <none>        5432/TCP   3h12m
```

## Install Trino
```bash
helm repo add trino https://trinodb.github.io/charts
helm upgrade --install trino -n trino -f deployment/trino/trino-values.yaml trino/trino --create-namespace --debug --version 0.21.0

k -n trino get po
k -n trino exec -it trino-coordinator-bd4568cd8-jn6sc trino
trino> CREATE SCHEMA lakehouse.raw WITH (location = 's3a://lakehouse/raw/');
trino> CREATE TABLE IF NOT EXISTS minio.raw.yellow_tripdata (
 vendor_name varchar,
 Trip_Pickup_DateTime varchar,
 Trip_Dropoff_DateTime varchar,
 Passenger_Count bigint,
 Trip_Distance double,
 Start_Lon double,
 Start_Lat double,
 Rate_Code double,
 store_and_forward double,
 End_Lon double,
 End_Lat double,
 Payment_Type Varchar,
 Fare_Amt double,
 surcharge double,
 mta_tax double,
 Tip_Amt double,
 Tolls_Amt double,
 Total_Amt double,
 y varchar,
 m varchar
)
WITH
(
    format = 'PARQUET',
    external_location = 's3a://lakehouse/raw/yellow_tripdata',
    partitioned_by = ARRAY[ 'y', 'm' ]
);

trino> CALL minio.system.sync_partition_metadata('raw', 'yellow_tripdata', 'FULL');

trino> CREATE TABLE IF NOT EXISTS lakehouse.raw.yellow_tripdata_trino_iceberg (
 vendor_name varchar,
 Trip_Pickup_DateTime varchar,
 Trip_Dropoff_DateTime varchar,
 Passenger_Count bigint,
 Trip_Distance double,
 Start_Lon double,
 Start_Lat double,
 Rate_Code double,
 store_and_forward double,
 End_Lon double,
 End_Lat double,
 Payment_Type Varchar,
 Fare_Amt double,
 surcharge double,
 mta_tax double,
 Tip_Amt double,
 Tolls_Amt double,
 Total_Amt double,
 y varchar,
 m varchar
)
WITH
(
    format = 'PARQUET',
    format_version = 2,
    partitioning = ARRAY[ 'y', 'm' ]
);

trino> insert into lakehouse.raw.yellow_tripdata_trino_iceberg
select * from lakehouse.raw.yellow_tripdata;
```

## Install Apache Doris

```bash
helm repo add doris https://charts.selectdb.com/
helm upgrade --install operator doris/doris-operator --namespace doris --create-namespace --debug --version 1.5.2
k apply -f ./doriscluster-sample-storageclass.yaml
k run mysql-client --image=mysql:5.7 -it --rm --restart=Never --namespace=doris -- /bin/bash

mysql -uroot -P9030 -hdoriscluster-sample-storageclass1-fe-service
mysql> SET PASSWORD FOR 'root' = PASSWORD('12345678');
mysql> SET PASSWORD FOR 'admin' = PASSWORD('12345678');

# Using dns not work => using ip
mysql> CREATE CATALOG iceberg PROPERTIES (
    "type"="iceberg",
    "iceberg.catalog.type"="hms",
    "hive.metastore.uris" = "thrift://10.96.46.36:9083",
    "warehouse" = "s3://lakehouse",
    "s3.access_key" = "admin",
    "s3.secret_key" = "password",
    "s3.endpoint" = "http://10.96.79.179:9000",
    "s3.region" = "us-east-1"
);
mysql> select * from iceberg.raw.yellow_tripdata_trino_iceberg limit 10;
```

## Destroy kind

```bash
kind delete cluster -n dev
```