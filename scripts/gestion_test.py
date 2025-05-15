import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.engine import engine
from services.write import load_token
from models import Event, User, Contract

db = Session(bind=engine)
token = load_token()

# 🔄 Test : associer un support à l'événement ID 1
event = db.query(Event).filter_by(id=1).first()
if not event:
    print("❌ Événement introuvable.")
else:
    new_support = db.query(User).filter_by(email="myrteza@example.com").first()
    if not new_support:
        print("❌ Utilisateur support non trouvé.")
    else:
        event.support_id = new_support.id
        db.commit()
        print(f"✅ Support modifié pour l'événement {event.id} → {new_support.name}")

# 🔄 Test : modifier un contrat existant (ID 1 ici)
contract = db.query(Contract).filter_by(id=1).first()
if not contract:
    print("❌ Contrat introuvable.")
else:
    contract.total_amount = 15000.0
    contract.amount_due = 5000.0
    contract.is_signed = False
    db.commit()
    print(f"✅ Contrat modifié : total={contract.total_amount}, dû={contract.amount_due}, signé={contract.is_signed}")
