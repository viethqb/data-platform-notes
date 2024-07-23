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
helm upgrade --install hive-metastore -n metastore -f deployment/hive/hive-metastore-values.yaml ../../charts/hive-metastore --create-namespace --debug

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
kubectl -n trino exec -it deployments/trino-coordinator trino 
trino> CREATE SCHEMA lakehouse.jaffle_shop WITH (location = 's3a://lakehouse/jaffle_shop.db/');
```

## Install Airflow
```bash
helm repo add airflow https://airflow.apache.org/
helm upgrade --install airflow airflow/airflow -f deployment/airflow/airflow-values.yaml --namespace airflow --create-namespace --debug --version 1.13.1 --timeout 600s
# Trigger: http://airflow.lakehouse.local/dags/dbt_jaffle-shop-classic_example/grid
```

## Install Apache Doris

```bash
helm repo add doris https://charts.selectdb.com/
helm upgrade --install operator doris/doris-operator --namespace doris --create-namespace --debug --version 1.6.0
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