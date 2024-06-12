## Create k8s cluster (kind)
```bash
kind create cluster --name dev --config deployment/kind/kind-config.yaml 
```
## Nginx ingress
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --set controller.hostNetwork=true,controller.service.type="",controller.kind=DaemonSet --namespace ingress-nginx --version 4.10.1 --create-namespace --debug --timeout 600s

k -n ingress-nginx get po -owide
```
## Install Minio on Kubernetes

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm upgrade --install minio -n minio -f deployment/minio/minio-values.yaml bitnami/minio --create-namespace --debug --version 14.6.0 --timeout 600s
kubectl -n minio get po
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
helm upgrade --install metastore-db -n metastore -f deployment/hive/hive-metastore-postgres-values.yaml bitnami/postgresql --create-namespace --debug --version 15.4.2 --timeout 600s
```
### Hive metastore
```bash
# docker pull rtdl/hive-metastore:3.1.2
# kind load docker-image rtdl/hive-metastore:3.1.2 --name dev
helm upgrade --install hive-metastore -n metastore -f deployment/hive/hive-metastore-values.yaml ../charts/hive-metastore --create-namespace --debug --timeout 600s
```

## Install Trino
```bash
helm repo add trino https://trinodb.github.io/charts
helm upgrade --install trino -n trino -f deployment/trino/trino-values.yaml trino/trino --create-namespace --debug --version 0.21.0 --timeout 600s

k -n trino get po
k -n trino exec -it trino-coordinator-b597bcd8c-f6vf7 trino 
trino> CREATE SCHEMA lakehouse.jaffle_shop WITH (location = 's3a://lakehouse/jaffle_shop/')
```

## Install Spark Operator

```bash
helm repo add spark-operator https://kubeflow.github.io/spark-operator 
helm upgrade --install spark-operator spark-operator/spark-operator --namespace spark-operator --set webhook.enable=true --set image.tag=v1beta2-1.4.6-3.5.0 --create-namespace --debug --version 1.3.2 --timeout 600s
```

## Install Airflow
```bash
helm repo add airflow https://airflow.apache.org/
helm upgrade --install airflow airflow/airflow -f deployment/airflow/airflow-values.yaml --namespace airflow --create-namespace --debug --version 1.13.1 --timeout 600s

# kubectl create secret generic airflow-ssh-secret --from-file=gitSshKey=/path/to/.ssh/airflowsshkey -n airflow
```
### Config S3 Connection and Kubernetes Connection in Airflow UI
```yaml
Connection Id: s3_default
Connection Type: Amazon Web Services
AWS Access Key ID: admin 
AWS Secret Access Key: password
Extra: {"endpoint_url": "http://minio.minio.svc.cluster.local:9000"}
```

```yaml
Connection Id: kubernetes_default
Connection Type: Kubernetes Cluster Connection
In cluster configuration: yes
Disable SSL: yes
```

### Config Airflow permission to submit Spark job
```bash
kubectl create role spark-operator-submitter --verb=create,get --resource=sparkapplications,pods/log --namespace=spark-operator
kubectl create rolebinding airflow-worker-spark-submitter --role=spark-operator-submitter --serviceaccount=airflow:airflow-worker --namespace=spark-operator 
```
## Destroy kind

```bash
kind delete cluster -n dev 
```