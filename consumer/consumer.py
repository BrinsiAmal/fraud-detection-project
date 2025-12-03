from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import time
from datetime import datetime

print("=" * 80)
print("🚨 SYSTÈME DE DÉTECTION DE FRAUDE AVEC ELASTICSEARCH")
print("=" * 80)

# Schéma des transactions
transaction_schema = StructType([
    StructField("transaction_id", IntegerType()),
    StructField("amount", DoubleType()),
    StructField("country", StringType()),
    StructField("client_id", IntegerType()),
    StructField("timestamp", StringType()),
    StructField("is_fraud", IntegerType())
])

# Créer SparkSession avec support Elasticsearch
spark = SparkSession.builder \
    .appName("FraudDetectionToElasticsearch") \
    .master("local[*]") \
    .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
            "org.elasticsearch:elasticsearch-spark-30_2.12:8.13.0") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
    .config("spark.ui.enabled", "true") \
    .config("spark.ui.port", "4040") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print(f"✅ Spark {spark.version} initialisé")
print(f"🌐 Spark UI: http://localhost:4040")

# Attendre que les services soient prêts
print("⏳ Attente des services...")
time.sleep(20)

# Test connexion Elasticsearch
try:
    # Tester Elasticsearch
    es_test_df = spark.createDataFrame([{"test": "connection"}])
    es_test_df.write \
        .format("org.elasticsearch.spark.sql") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.nodes.wan.only", "true") \
        .option("es.resource", "fraud-test/_doc") \
        .mode("append") \
        .save()
    print("✅ Connecté à Elasticsearch")
except Exception as e:
    print(f"⚠️  Note: Erreur connexion Elasticsearch (peut être normal au début): {e}")

# Lire depuis Kafka
print("📡 Connexion à Kafka...")
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "transactions") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

print("✅ Connecté à Kafka")

# Parser les données JSON
parsed_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), transaction_schema).alias("data")) \
    .select("data.*")

# Ajouter des métadonnées
enriched_df = parsed_df \
    .withColumn("processing_time", current_timestamp()) \
    .withColumn("fraud_severity", 
                col("amount") * col("is_fraud") / 1000) \
    .withColumn("alert_level",
                col("is_fraud").cast("string"))

# Filtrer uniquement les fraudes
fraud_df = enriched_df.filter(col("is_fraud") == 1)

print("\n" + "=" * 80)
print("🔴 FRAUDES DÉTECTÉES - Envoi vers Elasticsearch")
print("=" * 80)

# Fonction pour écrire dans Elasticsearch
def write_to_elasticsearch(batch_df, batch_id):
    try:
        if not batch_df.isEmpty():
            print(f"📝 Batch {batch_id}: {batch_df.count()} fraudes détectées")
            
            # Afficher dans la console
            batch_df.show(truncate=False)
            
            # Écrire dans Elasticsearch
            batch_df.write \
                .format("org.elasticsearch.spark.sql") \
                .option("es.nodes", "elasticsearch") \
                .option("es.port", "9200") \
                .option("es.nodes.wan.only", "true") \
                .option("es.resource", "fraud-alerts/_doc") \
                .option("es.mapping.id", "transaction_id") \
                .option("es.write.operation", "index") \
                .mode("append") \
                .save()
            
            print(f"✅ Batch {batch_id} envoyé à Elasticsearch")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi batch {batch_id}: {e}")

# Stream pour Elasticsearch
query_elastic = fraud_df.writeStream \
    .foreachBatch(write_to_elasticsearch) \
    .outputMode("append") \
    .start()

# Afficher aussi dans la console pour monitoring
query_console = fraud_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .option("numRows", 20) \
    .start()

# Stream pour statistiques (toutes les transactions)
from pyspark.sql.functions import window, count, sum, avg

stats_df = parsed_df \
    .withColumn("timestamp", col("timestamp").cast("timestamp")) \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(
        window(col("timestamp"), "1 minute"),
        "country"
    ) \
    .agg(
        count("*").alias("total_transactions"),
        sum("is_fraud").alias("fraud_count"),
        sum("amount").alias("total_amount"),
        avg("amount").alias("avg_amount")
    ) \
    .withColumn("fraud_rate", col("fraud_count") / col("total_transactions") * 100) \
    .withColumn("alert", col("fraud_rate") > 20) \
    .orderBy("window")

# Écrire les statistiques dans Elasticsearch
def write_stats_to_elastic(batch_df, batch_id):
    try:
        if not batch_df.isEmpty():
            batch_df.write \
                .format("org.elasticsearch.spark.sql") \
                .option("es.nodes", "elasticsearch") \
                .option("es.port", "9200") \
                .option("es.nodes.wan.only", "true") \
                .option("es.resource", "fraud-stats/_doc") \
                .option("es.write.operation", "index") \
                .mode("append") \
                .save()
    except Exception as e:
        print(f"⚠️  Erreur statistiques Elasticsearch: {e}")

query_stats = stats_df.writeStream \
    .foreachBatch(write_stats_to_elastic) \
    .outputMode("complete") \
    .trigger(processingTime="30 seconds") \
    .start()

print("\n" + "=" * 80)
print("🎯 SYSTÈME ACTIF")
print("=" * 80)
print("📊 Flux de données:")
print(" 1. Kafka → Spark Streaming")
print(" 2. Détection des fraudes")
print(" 3. Envoi vers Elasticsearch")
print(" 4. Visualisation dans Kibana")
print("")
print("🔗 Accès aux interfaces:")
print(" - Spark UI: http://localhost:4040")
print(" - Kibana: http://localhost:5601")
print(" - Elasticsearch: http://localhost:9200")
print("=" * 80)

# Attendre la fin des streams
query_elastic.awaitTermination()
