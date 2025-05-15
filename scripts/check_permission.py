import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.token import has_permission

# Lire le token depuis le fichier
with open(".token", "r") as f:
    token = f.read().strip()

# Demande une action à tester
action = input("Action à tester : ")

if has_permission(token, action):
    print(f"✅ Autorisé à faire '{action}'")
else:
    print(f"❌ Non autorisé à faire '{action}'")
