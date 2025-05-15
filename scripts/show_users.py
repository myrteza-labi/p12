import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.engine import engine
from models import User, Role

db = Session(bind=engine)

users = db.query(User).all()

print("📋 Liste des utilisateurs :\n")
for user in users:
    role = user.role.name if user.role else "Aucun rôle"
    print(f"- {user.name} | {user.email} | rôle : {role}")
