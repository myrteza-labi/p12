import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.engine import engine
from sqlalchemy.orm import Session
from services.read import load_token, get_all_clients, get_all_contracts, get_all_events

db = Session(bind=engine)
token = load_token()

print("\n📋 Clients :")
for c in get_all_clients(db, token):
    print("-", c.full_name)

print("\n📋 Contrats :")
for c in get_all_contracts(db, token):
    print("-", c.total_amount, "€ (restant :", c.amount_due, "€)")

print("\n📋 Événements :")
for e in get_all_events(db, token):
    print("-", e.location, "@", e.start_date)
