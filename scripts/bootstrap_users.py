# scripts/bootstrap_users.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.engine import engine
from sqlalchemy.orm import Session
from models.user import User
from models.role import Role
from services.auth import hash_password

def main():
    db = Session(bind=engine)
    # Crée les rôles s’ils n’existent pas
    for name in ("gestion","commercial","support"):
        if not db.query(Role).filter_by(name=name).first():
            db.add(Role(name=name))
    db.commit()

    users = [
        ("Admin Epic",       "admin@p12.fr",       "p12", "gestion"),
        ("Alice Gestion",    "gestion1@p12.fr",    "p12", "gestion"),
        ("Marc Gestion",     "gestion2@p12.fr",    "p12", "gestion"),
        ("Julie Commerciale","commercial1@p12.fr","p12","commercial"),
        ("Karim Commercial", "commercial2@p12.fr","p12","commercial"),
        ("Clara Support",    "support1@p12.fr",    "p12","support"),
        ("Thomas Support",   "support2@p12.fr",    "p12","support"),
    ]

    for full_name, email, pwd, role_name in users:
        if db.query(User).filter_by(email=email).first():
            continue
        role = db.query(Role).filter_by(name=role_name).first()
        user = User(
            name=full_name,
            email=email,
            password=hash_password(pwd),
            role_id=role.id
        )
        db.add(user)

    db.commit()
    print("✅ Tous les utilisateurs de base ont été créés.")

if __name__ == "__main__":
    main()
