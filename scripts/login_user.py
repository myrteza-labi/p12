import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.engine import engine
from sqlalchemy.orm import Session
from services.auth import login
from services.token import create_token

db = Session(bind=engine)

email = input("Email : ")
password = input("Mot de passe : ")

user = login(db, email, password)

if user:
    token = create_token(user.id, user.role.name)
    with open(".token", "w") as f:
        f.write(token)
    print(f"✅ Connexion réussie. Jeton sauvegardé.")
else:
    print("❌ Identifiants incorrects.")
