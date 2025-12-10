# 🚨 **Système de Détection de Fraude Bancaire en Temps Réel**

> Architecture Big Data complète pour l'analyse transactionnelle en temps réel utilisant Kafka, Spark Streaming et Elasticsearch

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Spark](https://img.shields.io/badge/Apache_Spark-3.5.1-orange.svg)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-3.4.1-black.svg)](https://kafka.apache.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.15.0-green.svg)](https://www.elastic.co/)
[![Docker](https://img.shields.io/badge/Docker-Containers-blue.svg)](https://www.docker.com/)

## 📋 **Aperçu du Projet**

Ce projet implémente un système complet de détection de fraude bancaire fonctionnant en **temps réel**. 
Il simule, traite et analyse des transactions financières pour identifier les activités suspectes en moins de 2 secondes.

### **✨ Fonctionnalités Principales**
- ✅ **Simulation réaliste** de transactions avec patterns de fraude intégrés
- ✅ **Détection en temps réel** avec latence < 2 secondes
- ✅ **Dashboard interactif** avec Kibana pour la visualisation
- ✅ **Architecture conteneurisée** prête à l'exécution
- ✅ **Monitoring complet** via Spark UI et logs
- ✅ **Scalabilité horizontale** conçue pour 10K+ transactions/sec

### **Composants**
1. **Producer** : Génère des transactions bancaires réalistes
2. **Kafka** : Bus de messages pour l'ingestion des données
3. **Spark Streaming** : Traitement distribué des transactions
4. **Elasticsearch** : Stockage et indexation des alertes
5. **Kibana** : Visualisation et dashboarding
6. **Zookeeper** : Coordination du cluster Kafka

## 🚀 **Démarrage Rapide**

### **Prérequis**
- Docker et Docker Compose installés
- 4GB de RAM minimum
- Python 3.11 (optionnel, pour développement)

### **Installation en 5 minutes**

# 1. Clonez le repository
git clone https://github.com/BrinsiAmal/fraud-detection-project.git
cd fraud-detection-project

# 2. Démarrez tous les services
docker-compose up -d

# 3. Vérifiez que tous les services tournent
docker-compose ps

# 4. Accédez aux interfaces
#    • Kibana : http://localhost:5601
#    • Spark UI : http://localhost:4040
#    • Elasticsearch : http://localhost:9200
