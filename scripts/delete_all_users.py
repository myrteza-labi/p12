import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.engine import engine
from models import User

# Connexion à la BDD
db = Session(bind=engine)

confirm = input("⚠️ Cette action va supprimer TOUS les utilisateurs (y compris les admins). Continuer ? (yes/no) : ").strip().lower()
if confirm not in ["yes", "y", "oui"]:
    print("❌ Annulé.")
    sys.exit()

users = db.query(User).all()

if not users:
    print("✅ Aucun utilisateur à supprimer.")
else:
    count = len(users)
    for user in users:
        db.delete(user)
    db.commit()
    print(f"✅ {count} utilisateur(s) supprimé(s).")
