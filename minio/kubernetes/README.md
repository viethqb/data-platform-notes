## Create k8s cluster (kind)
```bash
kind create cluster --name dev --config kind-config.yaml 
```

## Install Minio on Kubernetes

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm upgrade --install minio -n minio -f ./minio-values.yaml bitnami/minio --create-namespace --debug --version 14.6.0
kubectl -n minio get po
```

## Destroy kind

```bash
kind delete cluster -n dev 
```