import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.engine import engine
from models import User, Role

db = Session(bind=engine)

# Demande l'email de l'utilisateur à modifier
email = input("Email de l'utilisateur à modifier : ").strip()

# Recherche de l'utilisateur
user = db.query(User).filter_by(email=email).first()
if not user:
    print(f"❌ Aucun utilisateur trouvé avec l'email : {email}")
    db.close()
    exit()

print(f"\n🎯 Utilisateur trouvé : {user.name} ({user.email}) - rôle actuel : {user.role.name}")

# Champs à mettre à jour
new_name = input("Nouveau nom (laisser vide pour ne pas changer) : ").strip()
new_email = input("Nouvel email (laisser vide pour ne pas changer) : ").strip()
new_role = input("Nouveau rôle (gestion, commercial, support — laisser vide pour ne pas changer) : ").strip()

# Mise à jour des valeurs
if new_name:
    user.name = new_name
if new_email:
    user.email = new_email
if new_role:
    role = db.query(Role).filter_by(name=new_role).first()
    if not role:
        print(f"❌ Rôle '{new_role}' introuvable.")
        db.close()
        exit()
    user.role_id = role.id

db.commit()
print("✅ Utilisateur mis à jour avec succès.")
db.close()
