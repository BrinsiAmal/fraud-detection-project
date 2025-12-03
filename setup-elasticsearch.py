import requests
import json
import time

# Attendre Elasticsearch
print("⏳ Attente d'Elasticsearch...")
time.sleep(30)

ELASTICSEARCH_URL = "http://localhost:9200"

# Créer l'index pour les alertes de fraude
fraud_alerts_mapping = {
    "mappings": {
        "properties": {
            "transaction_id": {"type": "integer"},
            "amount": {"type": "double"},
            "country": {"type": "keyword"},
            "client_id": {"type": "integer"},
            "timestamp": {"type": "date"},
            "is_fraud": {"type": "integer"},
            "processing_time": {"type": "date"},
            "fraud_severity": {"type": "double"},
            "alert_level": {"type": "keyword"},
            "merchant_category": {"type": "keyword"},
            "payment_method": {"type": "keyword"},
            "device_type": {"type": "keyword"},
            "ip_country": {"type": "keyword"}
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

# Créer l'index pour les statistiques
fraud_stats_mapping = {
    "mappings": {
        "properties": {
            "window": {
                "properties": {
                    "start": {"type": "date"},
                    "end": {"type": "date"}
                }
            },
            "country": {"type": "keyword"},
            "total_transactions": {"type": "integer"},
            "fraud_count": {"type": "integer"},
            "total_amount": {"type": "double"},
            "avg_amount": {"type": "double"},
            "fraud_rate": {"type": "double"},
            "alert": {"type": "boolean"}
        }
    }
}

# Créer les indices
indices = {
    "fraud-alerts": fraud_alerts_mapping,
    "fraud-stats": fraud_stats_mapping
}

for index_name, mapping in indices.items():
    try:
        # Supprimer l'index s'il existe
        requests.delete(f"{ELASTICSEARCH_URL}/{index_name}", timeout=5)
        
        # Créer le nouvel index
        response = requests.put(
            f"{ELASTICSEARCH_URL}/{index_name}",
            json=mapping,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Index '{index_name}' créé avec succès")
        else:
            print(f"⚠️  Erreur création index '{index_name}': {response.text}")
    except Exception as e:
        print(f"❌ Erreur avec index '{index_name}': {e}")

print("\n🎯 Configuration Elasticsearch terminée!")
print(f"🔗 Accès: {ELASTICSEARCH_URL}")
print("   Indices créés:")
print("   - fraud-alerts: Alertes de fraude individuelles")
print("   - fraud-stats: Statistiques agrégées")