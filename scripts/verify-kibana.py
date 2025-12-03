#!/usr/bin/env python3
"""
Vérifier que Kibana est bien configuré
"""

import requests

def verify_kibana():
    print("🔍 Vérification Kibana...")
    
    # Vérifier connexion
    try:
        resp = requests.get("http://localhost:5601/api/status", timeout=5)
        print(f"✅ Kibana accessible - Status: {resp.status_code}")
    except:
        print("❌ Kibana inaccessible")
        return
    
    # Vérifier index patterns
    try:
        resp = requests.get(
            "http://localhost:5601/api/saved_objects/_find?type=index-pattern",
            headers={"kbn-xsrf": "true"},
            timeout=5
        )
        patterns = resp.json()
        
        fraud_patterns = [p for p in patterns['saved_objects'] if 'fraud' in p['attributes']['title']]
        
        if fraud_patterns:
            print("✅ Index patterns fraud trouvés:")
            for p in fraud_patterns:
                print(f"   • {p['attributes']['title']}")
        else:
            print("⚠️  Aucun index pattern fraud trouvé")
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")

if __name__ == "__main__":
    verify_kibana()