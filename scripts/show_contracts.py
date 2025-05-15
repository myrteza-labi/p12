# scripts/show_contracts.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.engine import engine
from models import Contract, Client, User

db = Session(bind=engine)
contracts = db.query(Contract).all()

for c in contracts:
    client = db.query(Client).get(c.client_id)
    commercial = db.query(User).get(c.commercial_id)
    print(f"🆔 {c.id} | Client: {client.full_name} | Commercial: {commercial.name} | Montant: {c.total_amount} | Signé: {c.is_signed}")
