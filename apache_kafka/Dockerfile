FROM confluentinc/cp-kafka-connect:7.6.1 as cp
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-s3:10.5.12
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-avro-converter:7.6.1
FROM quay.io/strimzi/kafka:0.41.0-kafka-3.7.0
USER root:root
# Add S3 dependency
COPY --from=cp /usr/share/confluent-hub-components/confluentinc-kafka-connect-s3/ /opt/kafka/plugins/kafka-connect-s3/