#!/bin/bash

echo "🔧 Configuration Kibana pour la détection de fraude"
echo "=================================================="

# Attendre Kibana
echo "⏳ Attente de Kibana..."
sleep 60

# Créer l'index pattern pour fraud-alerts
echo "📊 Création index pattern fraud-alerts..."
curl -X POST "http://localhost:5601/api/saved_objects/index-pattern/fraud-alerts" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "fraud-alerts*",
      "timeFieldName": "processing_time"
    }
  }'

echo -e "\n"

# Créer l'index pattern pour fraud-stats
echo "📈 Création index pattern fraud-stats..."
curl -X POST "http://localhost:5601/api/saved_objects/index-pattern/fraud-stats" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "fraud-stats*",
      "timeFieldName": "window.start"
    }
  }'

echo -e "\n"

echo "✅ Configuration terminée !"
echo "🔗 Accès : http://localhost:5601"
echo "📋 Pour voir vos données :"
echo "   1. Aller à http://localhost:5601"
echo "   2. Cliquer sur ☰ Menu → Discover"
echo "   3. Sélectionner 'fraud-alerts*'"