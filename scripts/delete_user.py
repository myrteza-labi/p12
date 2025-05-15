# scripts/delete_user.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy.orm import Session
from database.engine import engine
from models import User

db = Session(bind=engine)
user = db.query(User).filter_by(email=" support@example.com").first()
if user:
    db.delete(user)
    db.commit()
    print("✅ Utilisateur supprimé.")
else:
    print("❌ Utilisateur introuvable.")
