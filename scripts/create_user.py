import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.engine import engine
from sqlalchemy.orm import Session
from models import User, Role
from services.auth import hash_password

# Connexion à la BDD
db = Session(bind=engine)

# Inputs dynamiques
name = input("Nom complet : ")
email = input("Email : ")
password = input("Mot de passe : ")
role_name = input("Rôle (gestion, commercial, support) : ").strip()

# On récupère (ou crée) le rôle demandé
role = db.query(Role).filter(Role.name == role_name).first()
if not role:
    role = Role(name=role_name)
    db.add(role)
    db.commit()
    db.refresh(role)

# Vérifie doublon
existing_user = db.query(User).filter_by(email=email).first()
if existing_user:
    print(f"⚠️ Utilisateur avec l'email {email} existe déjà.")
else:
    # Création de l'utilisateur
    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role_id=role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("✅ Utilisateur créé avec succès :", user.name)
