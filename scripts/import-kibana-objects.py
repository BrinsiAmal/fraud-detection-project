#!/usr/bin/env python3
"""
Importer des objets Kibana depuis des fichiers JSON
"""

import requests
import json
import os
import glob

KIBANA_URL = "http://localhost:5601"
HEADERS = {
    "kbn-xsrf": "true",
    "Content-Type": "application/json"
}

def import_object(file_path, object_type):
    """Importer un objet dans Kibana"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        object_id = data.get('attributes', {}).get('title', os.path.basename(file_path).replace('.json', ''))
        
        response = requests.post(
            f"{KIBANA_URL}/api/saved_objects/{object_type}/{object_id}",
            json=data,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ {object_type.capitalize()} importé: {object_id}")
            return True
        else:
            print(f"⚠️  Erreur import {object_id}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lecture {file_path}: {e}")
        return False

def main():
    print("📤 Import Kibana objects")
    print("=" * 50)
    
    # Définir l'ordre d'import
    import_order = [
        ("index-pattern", "fraud-alerts*.json"),
        ("index-pattern", "fraud-stats*.json"),
        ("visualization", "*.json"),
        ("dashboard", "*.json")
    ]
    
    for obj_type, pattern in import_order:
        files = glob.glob(f"kibana-exports/{pattern}")
        for file in files:
            if "fraud" in file.lower():  # Importer seulement les objets fraud
                import_object(file, obj_type.split('-')[0] if '-' in obj_type else obj_type)
    
    print("\n✅ Import terminé")
    print(f"🔗 Accès : {KIBANA_URL}")

if __name__ == "__main__":
    main()