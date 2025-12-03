from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime
import socket

def wait_for_service(host, port, service_name, max_retries=30):
    """Attendre qu'un service soit disponible"""
    for i in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                print(f"✅ {service_name} disponible")
                return True
            else:
                print(f"⏳ Attente {service_name}... ({i+1}/{max_retries})")
        except Exception:
            pass
        time.sleep(2)
    print(f"❌ {service_name} non disponible")
    return False

def generate_transaction(transaction_id):
    """Génère une transaction réaliste avec patterns de fraude"""
    
    # Pays avec différents niveaux de risque
    high_risk_countries = ["UAE", "US", "RU"]
    medium_risk_countries = ["UK", "DE", "FR"]
    low_risk_countries = ["TN", "CA", "AU", "JP"]
    
    all_countries = high_risk_countries + medium_risk_countries + low_risk_countries
    country = random.choice(all_countries)
    
    # Générer montant avec différentes distributions
    if random.random() < 0.1:  # 10% de transactions très élevées
        amount = round(random.uniform(5000, 50000), 2)
    elif random.random() < 0.3:  # 30% de transactions élevées
        amount = round(random.uniform(1000, 5000), 2)
    else:  # 60% de transactions normales
        amount = round(random.uniform(10, 1000), 2)
    
    # Logique de détection de fraude
    is_fraud = 0
    
    # Pattern 1: Transactions très élevées depuis pays à risque
    if amount > 8000 and country in high_risk_countries:
        is_fraud = 1 if random.random() < 0.8 else 0
    
    # Pattern 2: Transactions rapides et répétées
    elif amount > 3000 and random.random() < 0.3:
        is_fraud = 1
    
    # Pattern 3: Transactions hors heures normales
    current_hour = datetime.now().hour
    if current_hour < 6 or current_hour > 22:  # Nuit
        if amount > 2000:
            is_fraud = 1 if random.random() < 0.5 else 0
    
    # Pattern 4: Montants ronds (souvent frauduleux)
    if amount % 100 == 0 and amount > 1000:
        is_fraud = 1 if random.random() < 0.4 else 0
    
    # Base rate: 5% de fraude aléatoire
    if random.random() < 0.05:
        is_fraud = 1
    
    return {
        "transaction_id": transaction_id,
        "amount": amount,
        "country": country,
        "client_id": random.randint(1, 10000),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "is_fraud": is_fraud,
        "merchant_category": random.choice(["retail", "travel", "digital", "services", "entertainment"]),
        "payment_method": random.choice(["credit_card", "debit_card", "paypal", "bank_transfer"]),
        "device_type": random.choice(["mobile", "desktop", "tablet"]),
        "ip_country": country
    }

def main():
    print("=" * 70)
    print("🏦 SIMULATEUR DE TRANSACTIONS BANCAIRES")
    print("=" * 70)
    
    # Attendre les services
    print("🔍 Vérification des services...")
    
    services = [
        ("kafka", 9092, "Kafka"),
        ("elasticsearch", 9200, "Elasticsearch")
    ]
    
    for host, port, name in services:
        if not wait_for_service(host, port, name):
            print(f"⚠️  Continuation sans {name}")
    
    # Créer le producer Kafka
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
            linger_ms=10,
            batch_size=32768
        )
        print("✅ Producteur Kafka initialisé")
    except Exception as e:
        print(f"❌ Erreur producteur: {e}")
        return
    
    print("\n🚀 Démarrage de la simulation...")
    print("-" * 70)
    
    transaction_id = 1000000
    count = 0
    fraud_count = 0
    total_amount = 0
    
    try:
        while True:
            # Générer transaction
            transaction = generate_transaction(transaction_id)
            
            # Envoyer à Kafka
            producer.send('transactions', transaction)
            
            # Statistiques
            count += 1
            transaction_id += 1
            total_amount += transaction['amount']
            
            if transaction['is_fraud'] == 1:
                fraud_count += 1
                print(f"🚨 FRAUDE #{fraud_count:03d}: "
                      f"{transaction['amount']:9,.2f}€ "
                      f"({transaction['country']:3}) "
                      f"[{transaction['merchant_category']:10}] "
                      f"ID: {transaction['transaction_id']}")
            else:
                if count % 10 == 0:
                    print(f"✅ Transaction #{count:04d}: "
                          f"{transaction['amount']:9,.2f}€ "
                          f"({transaction['country']:3})")
            
            # Délai réaliste
            if transaction['is_fraud'] == 1:
                time.sleep(random.uniform(0.05, 0.3))
            else:
                time.sleep(random.uniform(0.1, 1.5))
            
            # Afficher statistiques toutes les 50 transactions
            if count % 50 == 0:
                print("\n" + "-" * 70)
                print(f"📊 STATISTIQUES INTERMÉDIAIRES")
                print(f"   Transactions totales: {count}")
                print(f"   Fraudes détectées: {fraud_count}")
                if count > 0:
                    print(f"   Taux de fraude: {fraud_count/count*100:.2f}%")
                    print(f"   Montant moyen: {total_amount/count:,.2f}€")
                print("-" * 70 + "\n")
                
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("📈 RAPPORT FINAL")
        print("=" * 70)
        print(f"   Transactions générées: {count}")
        print(f"   Alertes de fraude: {fraud_count}")
        if count > 0:
            print(f"   Taux de fraude: {fraud_count/count*100:.2f}%")
            print(f"   Montant total: {total_amount:,.2f}€")
            print(f"   Montant moyen: {total_amount/count:,.2f}€")
        print("=" * 70)
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()

