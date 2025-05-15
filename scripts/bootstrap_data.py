# scripts/bootstrap_data.py
import sys, os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.engine import engine
from sqlalchemy.orm import Session
from models.client import Client
from models.contract import Contract
from models.event import Event
from models.user import User


def main():
    db = Session(bind=engine)

    # --- Clients ---
    clients_data = [
        {
            "full_name": "Kevin Casey",
            "email": "client1@p12.fr",
            "phone": "+67812345678",
            "company_name": "Cool Startup LLC",
            "created_date": datetime(2021, 4, 18).date(),
            "last_contact_date": datetime(2023, 3, 29).date(),
            "commercial_email": "commercial1@p12.fr"
        },
        {
            "full_name": "Lou Bouzin",
            "email": "client2@p12.fr",
            "phone": "+66612345",
            "company_name": "Lou Bouzin Group",
            "created_date": datetime(2023, 1, 10).date(),
            "last_contact_date": datetime(2023, 5, 1).date(),
            "commercial_email": "commercial2@p12.fr"
        },
        {
            "full_name": "Sofia Lemoine",
            "email": "client3@p12.fr",
            "phone": "+33655987321",
            "company_name": "Artivisuel",
            "created_date": datetime(2022, 7, 20).date(),
            "last_contact_date": datetime(2023, 4, 2).date(),
            "commercial_email": "commercial1@p12.fr"
        }
    ]

    for data in clients_data:
        existing = db.query(Client).filter_by(email=data["email"]).first()
        if existing:
            continue
        # find commercial id
        commercial = db.query(User).filter_by(email=data["commercial_email"]).first()
        client = Client(
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            company_name=data["company_name"],
            created_date=data["created_date"],
            last_contact_date=data["last_contact_date"],
            commercial_id=commercial.id if commercial else None
        )
        db.add(client)
    db.commit()

    # --- Contracts ---
    contracts_data = [
        {
            "client_email": "client1@p12.fr",
            "commercial_email": "commercial1@p12.fr",
            "total_amount": 5000.0,
            "amount_due": 0.0,
            "is_signed": True,
            "created_date": datetime(2023, 2, 1).date()
        },
        {
            "client_email": "client2@p12.fr",
            "commercial_email": "commercial2@p12.fr",
            "total_amount": 12000.0,
            "amount_due": 4000.0,
            "is_signed": False,
            "created_date": datetime(2023, 3, 1).date()
        }
    ]

    for data in contracts_data:
        client = db.query(Client).filter_by(email=data["client_email"]).first()
        commercial = db.query(User).filter_by(email=data["commercial_email"]).first()
        existing = db.query(Contract).filter_by(client_id=client.id, commercial_id=commercial.id).first()
        if existing:
            continue
        contract = Contract(
            total_amount=data["total_amount"],
            amount_due=data["amount_due"],
            is_signed=data["is_signed"],
            created_date=data["created_date"],
            client_id=client.id,
            commercial_id=commercial.id
        )
        db.add(contract)
    db.commit()

    # --- Events ---
    events_data = [
        {
            "contract_idx": 0,  # index in contracts_data
            "client_email": "client1@p12.fr",
            "support_email": "support1@p12.fr",
            "start_date": datetime(2023, 6, 4, 13, 0),
            "end_date": datetime(2023, 6, 5, 2, 0),
            "location": "53 Rue du Château, 41120 Candé-sur-Beuvron",
            "attendees": 75,
            "notes": "DJ à organiser par Clara."
        },
        {
            "contract_idx": 1,
            "client_email": "client2@p12.fr",
            "support_email": "support2@p12.fr",
            "start_date": datetime(2023, 5, 5, 15, 0),
            "end_date": datetime(2023, 5, 5, 17, 0),
            "location": "Salle des fêtes de Mufflins",
            "attendees": 200,
            "notes": "AG des actionnaires"
        }
    ]

    contracts = db.query(Contract).order_by(Contract.id).all()
    for data in events_data:
        contract = contracts[data["contract_idx"]]
        client = db.query(Client).filter_by(email=data["client_email"]).first()
        support = db.query(User).filter_by(email=data["support_email"]).first()
        existing = db.query(Event).filter_by(contract_id=contract.id).first()
        if existing:
            continue
        event = Event(
            contract_id=contract.id,
            client_id=client.id,
            support_id=support.id,
            start_date=data["start_date"],
            end_date=data["end_date"],
            location=data["location"],
            attendees=data["attendees"],
            notes=data["notes"]
        )
        db.add(event)
    db.commit()

    print("✅ Données clients, contrats et événements initialisées.")

if __name__ == "__main__":
    main()