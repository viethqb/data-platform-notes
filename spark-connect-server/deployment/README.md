## Create k8s cluster (kind)
```bash
kind create cluster --name dev --config ./kind-config.yaml 
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
helm upgrade --install minio -n minio -f minio/minio-values.yaml bitnami/minio --create-namespace --debug --version 14.6.0
kubectl -n minio get po
kubectl get no -owide
# NAME                STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION     CONTAINER-RUNTIME
# dev-control-plane   Ready    control-plane   22m   v1.30.0   172.25.0.2    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15
# dev-worker          Ready    <none>          21m   v1.30.0   172.25.0.4    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15
# dev-worker2         Ready    <none>          21m   v1.30.0   172.25.0.3    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15
# dev-worker3         Ready    <none>          21m   v1.30.0   172.25.0.5    <none>        Debian GNU/Linux 12 (bookworm)   6.5.0-28-generic   containerd://1.7.15

# Add the following lines to the end of the /etc/hosts
# 172.25.0.4  minio.lakehouse.localls
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
helm upgrade --install metastore-db -n metastore -f hive/hive-metastore-postgres-values.yaml bitnami/postgresql --create-namespace --debug --version 15.4.2
```
### Hive metastore
```bash
# docker pull rtdl/hive-metastore:3.1.2
# kind load docker-image rtdl/hive-metastore:3.1.2 --name dev
helm upgrade --install hive-metastore -n metastore -f hive/hive-metastore-values.yaml ../charts/hive-metastore --create-namespace --debug
```

## Install Trino
```bash
helm repo add trino https://trinodb.github.io/charts
helm upgrade --install trino -n trino -f trino/trino-values.yaml trino/trino --create-namespace --debug --version 0.21.0

k -n trino get po
```

## Install Spark Connect Server

```bash
kubectl create ns sparglim
kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts
kubectl apply -f spark-connect-server/
```

## Destroy kind

```bash
kind delete cluster -n dev 
```