FROM confluentinc/cp-kafka-connect:7.6.1 as cp
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-s3:10.5.12
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-avro-converter:7.6.1
RUN confluent-hub install --no-prompt tabular/iceberg-kafka-connect:0.6.18
RUN confluent-hub install --no-prompt debezium/debezium-connector-mysql:2.4.2
RUN confluent-hub install --no-prompt debezium/debezium-connector-postgresql:2.5.4
RUN confluent-hub install --no-prompt debezium/debezium-connector-sqlserver:2.5.4
RUN confluent-hub install --no-prompt debezium/debezium-connector-mongodb:2.4.2
FROM quay.io/strimzi/kafka:0.41.0-kafka-3.7.0
USER root:root
# Add S3 dependency
COPY --from=cp /usr/share/confluent-hub-components/confluentinc-kafka-connect-s3/ /opt/kafka/plugins/kafka-connect-s3/
# Add Avro Converter dependency
COPY --from=cp /usr/share/confluent-hub-components/confluentinc-kafka-connect-avro-converter/ /opt/kafka/plugins/confluentinc-kafka-connect-avro-converter/
# Add Iceberg dependency
COPY --from=cp /usr/share/confluent-hub-components/tabular-iceberg-kafka-connect/ /opt/kafka/plugins/tabular-iceberg-kafka-connect/
# Add debezium-connector-mysql 
COPY --from=cp /usr/share/confluent-hub-components/debezium-debezium-connector-mysql/ /opt/kafka/plugins/debezium-debezium-connector-mysql/
# Add debezium-connector-postgresql 
COPY --from=cp /usr/share/confluent-hub-components/debezium-debezium-connector-postgresql/ /opt/kafka/plugins/debezium-debezium-connector-postgresql/
# Add debezium-connector-sqlserver 
COPY --from=cp /usr/share/confluent-hub-components/debezium-debezium-connector-sqlserver/ /opt/kafka/plugins/debezium-debezium-connector-sqlserver/
# Add debezium-connector-mongodb 
COPY --from=cp /usr/share/confluent-hub-components/debezium-debezium-connector-mongodb/ /opt/kafka/plugins/debezium-debezium-connector-mongodb/