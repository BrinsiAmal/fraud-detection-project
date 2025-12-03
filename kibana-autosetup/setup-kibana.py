#!/usr/bin/env python3
"""
Configuration simple de Kibana
"""

import requests
import time
import sys

print("🔧 Configuration simple de Kibana...")

# Attendre Kibana
print("⏳ Attente de Kibana...")
for i in range(30):
    try:
        resp = requests.get("http://localhost:5601/api/status", timeout=5)
        if resp.status_code == 200:
            print("✅ Kibana prêt")
            break
    except:
        pass
    time.sleep(2)
else:
    print("❌ Kibana non disponible")
    sys.exit(1)

# Créer les index patterns
headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}

index_patterns = [
    {"title": "fraud-alerts*", "timeField": "processing_time"},
    {"title": "fraud-stats*", "timeField": "window.start"}
]

for pattern in index_patterns:
    try:
        resp = requests.post(
            f"http://localhost:5601/api/saved_objects/index-pattern/{pattern['title'].replace('*', 'all')}",
            json={
                "attributes": {
                    "title": pattern["title"],
                    "timeFieldName": pattern["timeField"]
                }
            },
            headers=headers,
            timeout=10
        )
        if resp.status_code in [200, 201, 409]:
            print(f"✅ Index pattern: {pattern['title']}")
        else:
            print(f"⚠️  {pattern['title']}: {resp.status_code}")
    except Exception as e:
        print(f"⚠️  Erreur {pattern['title']}: {e}")

print("\n🎯 Configuration terminée!")
print("🔗 Accès: http://localhost:5601")
print("   → Menu ☰ → Discover → Sélectionnez 'fraud-alerts*'")