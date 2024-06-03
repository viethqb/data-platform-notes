## Install Kafka

### Install Strimzi Operator

```bash
helm repo add strimzi https://strimzi.io/charts/
helm install kafka-operator strimzi/strimzi-kafka-operator --namespace=kafka --create-namespace --debug --version 0.41.0
```

### Create Kafka Cluster

```bash
kubectl apply -f kafka-persistent-single.yaml
```
