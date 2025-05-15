# services/read.py

import sentry_sdk
from sqlalchemy.orm import Session
from models.client import Client
from models.contract import Contract
from models.event import Event

def load_token(path=".token"):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ Jeton introuvable.")
        return None

def get_all_clients(db: Session, token: str):
    """Récupère tous les clients (lecture seule, tous les rôles)."""
    try:
        return db.query(Client).all()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print("❌ Erreur lors de la récupération des clients.")
        return []

def get_all_contracts(db: Session, token: str):
    """Récupère tous les contrats (lecture seule, tous les rôles)."""
    try:
        return db.query(Contract).all()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print("❌ Erreur lors de la récupération des contrats.")
        return []

def get_all_events(db: Session, token: str):
    """Récupère tous les événements (lecture seule, tous les rôles)."""
    try:
        return db.query(Event).all()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print("❌ Erreur lors de la récupération des événements.")
        return []
