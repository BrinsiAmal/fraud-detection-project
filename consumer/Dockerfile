FROM apache/spark:3.5.1

USER root

# Installer les dépendances Elasticsearch
RUN pip3 install --no-cache-dir \
    kafka-python==2.0.2 \
    elasticsearch==8.13.0

WORKDIR /app
COPY consumer.py .

CMD ["/opt/spark/bin/spark-submit", \
     "--master", "local[*]", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.13.0", \
     "--conf", "spark.sql.streaming.checkpointLocation=/tmp/checkpoint", \
     "--conf", "spark.ui.enabled=true", \
     "--conf", "spark.ui.port=4040", \
     "--conf", "spark.driver.bindAddress=0.0.0.0", \
     "consumer.py"]

