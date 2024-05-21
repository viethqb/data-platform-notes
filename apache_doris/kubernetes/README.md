## Create Kubernetes Local Cluster (Using Kind)

```bash
kind create cluster --name dev --config kind-config.yaml
```

## Install Apache Doris

```bash
helm upgrade --install operator ../../charts/doris-operator --namespace doris --create-namespace --debug
k apply -f ./doriscluster-sample-storageclass.yaml
k run mysql-client --image=mysql:5.7 -it --rm --restart=Never --namespace=doris -- /bin/bash

mysql -uroot -P9030 -hdoriscluster-sample-storageclass1-fe-service
mysql> SET PASSWORD FOR 'root' = PASSWORD('12345678');
mysql> SET PASSWORD FOR 'admin' = PASSWORD('12345678');
mysql> CREATE CATALOG iceberg PROPERTIES (
    "type"="iceberg",
    "iceberg.catalog.type"="hms",
    "hive.metastore.uris" = "thrift://10.96.53.242:9083",
    "warehouse" = "s3://lakehouse",
    "s3.access_key" = "admin",
    "s3.secret_key" = "password",
    "s3.endpoint" = "http://10.96.108.45:9000",
    "s3.region" = "us-east-1"
);
mysql> select vendor_name, trip_pickup_datetime from iceberg.nyc.taxis_large limit 10;
```