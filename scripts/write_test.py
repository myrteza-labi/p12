import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.engine import engine
from services.write import load_token, create_user, create_client, create_contract, create_event
from models.role import Role

db = Session(bind=engine)
token = load_token()

# Crée le rôle 'commercial' s'il n'existe pas déjà
if not db.query(Role).filter_by(name="commercial").first():
    db.add(Role(name="commercial"))
    db.commit()
    print("✅ Rôle 'commercial' ajouté.")

# Test : ajouter un collaborateur
create_user(db, token, "Alice Dupont", "alice@example.com", "motdepasse", "commercial")

# Test : ajouter un client
create_client(db, token, "Kevin Casey", "kevin@startup.io")

# Test : ajouter un contrat
create_contract(
    db,
    token,
    client_email="kevin@startup.io",
    commercial_email="alice@example.com",
    total_amount=10000.0,
    amount_due=2500.0,
    is_signed=True
)

# Test : ajouter un événement
create_event(
    db,
    token,
    contract_id=1,  # change si besoin
    client_email="kevin@startup.io",
    support_email="myrteza@example.com",  # assure-toi que ce user existe
    start_date="2025-06-01 14:00",
    end_date="2025-06-01 20:00",
    location="53 Rue du Château, 41120 Candé-sur-Beuvron",
    attendees=75,
    notes="DJ à prévoir, buffet prêt à 17h."
)
