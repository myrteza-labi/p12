import sys, os
from sqlalchemy.orm import Session
from services.token import decode_token, has_permission
from models.user import User
from models.role import Role
from models.client import Client
from models.contract import Contract
from models.event import Event
from datetime import datetime
import sentry_sdk
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ▶ Créer un utilisateur
def create_user(db: Session, token: str, name: str, email: str, password: str, role_name: str):
    if not has_permission(token, "create_user"):
        print("❌ Permission refusée : create_user")
        return
    role = db.query(Role).filter_by(name=role_name).first()
    if not role:
        print(f"❌ Rôle '{role_name}' introuvable.")
        return
    existing = db.query(User).filter_by(email=email).first()
    if existing:
        print(f"⚠️ Utilisateur avec l'email {email} existe déjà.")
        return
    hashed_password = pwd_context.hash(password)
    user = User(name=name, email=email, password=hashed_password, role_id=role.id)
    db.add(user)
    db.commit()
    print(f"✅ Collaborateur '{name}' ajouté avec succès.")
    sentry_sdk.capture_message(f"Utilisateur {email} créé")

# ▶ Créer un client
def create_client(db: Session, token: str, full_name: str, email: str):
    # Vérification des permissions
    if not has_permission(token, "create_client") and not has_permission(token, "view_all"):
        print("❌ Permission refusée : create_client")
        return

    # Décoder le token pour récupérer l'ID du commercial courant
    payload = decode_token(token)
    if not payload:
        print("❌ Jeton invalide ou expiré.")
        return
    commercial_id = payload.get("user_id")

    # Empêcher doublons
    if db.query(Client).filter_by(email=email).first():
        print(f"⚠️ Client avec l'email {email} existe déjà.")
        return

    # Création du client avec dates et association commerciale
    today = datetime.utcnow().date()
    client = Client(
        full_name=full_name,
        email=email,
        phone=None,
        company_name=None,
        created_date=today,
        last_contact_date=today,
        commercial_id=commercial_id
    )
    db.add(client)
    db.commit()

    print(f"✅ Client '{full_name}' ajouté avec succès (commercial_id={commercial_id}).")
    sentry_sdk.capture_message(f"Client {email} créé par user_id={commercial_id}")


# ▶ Créer un contrat
def create_contract(db: Session, token: str, client_email: str, commercial_email: str, total_amount: float, amount_due: float, is_signed: bool):
    if not has_permission(token, "create_contract"):
        print("❌ Permission refusée : create_contract")
        return
    client = db.query(Client).filter_by(email=client_email).first()
    if not client:
        print(f"❌ Client avec l'email {client_email} introuvable.")
        return
    commercial = db.query(User).filter_by(email=commercial_email).first()
    if not commercial:
        print(f"❌ Commercial avec l'email {commercial_email} introuvable.")
        return
    contract = Contract(
        total_amount=total_amount,
        amount_due=amount_due,
        is_signed=is_signed,
        created_date=datetime.utcnow().date(),
        client_id=client.id,
        commercial_id=commercial.id
    )
    db.add(contract)
    db.commit()
    print(f"✅ Contrat pour '{client.full_name}' créé avec succès.")
    sentry_sdk.capture_message(f"Contrat pour {client_email} créé")

# ▶ Créer un événement
def create_event(
    db: Session,
    token: str,
    contract_id: int,
    client_email: str,
    support_email: str,
    start_date: str,
    end_date: str,
    location: str,
    attendees: int,
    notes: str
):
    if not has_permission(token, "create_event"):
        print("❌ Permission refusée : create_event")
        return
    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        print(f"❌ Contrat avec l'ID {contract_id} introuvable.")
        return
    if not contract.is_signed:
        print("❌ Impossible de créer un événement : le contrat n'est pas signé.")
        return
    client = db.query(Client).filter_by(email=client_email).first()
    if not client:
        print(f"❌ Client avec l'email {client_email} introuvable.")
        return
    support = db.query(User).filter_by(email=support_email).first()
    if not support:
        print(f"❌ Utilisateur support '{support_email}' introuvable.")
        return
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        if start >= end:
            print("❌ La date de fin doit être postérieure à la date de début.")
            return
    except ValueError:
        print("❌ Format de date invalide. Utilise YYYY-MM-DD HH:MM")
        return
    event = Event(
        contract_id=contract.id,
        client_id=client.id,
        support_id=support.id,
        start_date=start,
        end_date=end,
        location=location,
        attendees=attendees,
        notes=notes
    )
    db.add(event)
    db.commit()
    print(f"✅ Événement pour '{client.full_name}' créé avec succès.")
    sentry_sdk.capture_message(f"Événement pour {client_email} créé")

# Mettre à jour un collaborateur
def update_user(db: Session, token: str, user_id: int, name: str = None, email: str = None, role_name: str = None):
    if not has_permission(token, 'update_user'):
        print("❌ Permission refusée : update_user")
        return
    user = db.query(User).get(user_id)
    if not user:
        print(f"❌ Utilisateur ID {user_id} introuvable.")
        return
    if name:
        user.name = name
    if email:
        user.email = email
    if role_name:
        role = db.query(Role).filter_by(name=role_name).first()
        if not role:
            print(f"❌ Rôle '{role_name}' introuvable.")
            return
        user.role_id = role.id
    db.commit()
    print(f"✅ Utilisateur ID {user_id} mis à jour.")
    sentry_sdk.capture_message(f"Utilisateur {user_id} mis à jour")

# Supprimer un collaborateur
def delete_user(db: Session, token: str, user_id: int):
    if not has_permission(token, 'delete_user'):
        print("❌ Permission refusée : delete_user")
        return
    user = db.query(User).get(user_id)
    if not user:
        print(f"❌ Utilisateur ID {user_id} introuvable.")
        return
    db.delete(user)
    db.commit()
    print(f"✅ Utilisateur ID {user_id} supprimé.")
    sentry_sdk.capture_message(f"Utilisateur {user_id} supprimé")

# Mettre à jour un client
def update_client(db: Session, token: str, client_id: int, full_name: str = None, email: str = None, phone: str = None):
    if not has_permission(token, 'update_client'):
        print("❌ Permission refusée : update_client")
        return
    client = db.query(Client).get(client_id)
    if not client:
        print(f"❌ Client ID {client_id} introuvable.")
        return
    if full_name:
        client.full_name = full_name
    if email:
        client.email = email
    if phone:
        client.phone = phone
    client.last_contact_date = datetime.utcnow().date()
    db.commit()
    print(f"✅ Client ID {client_id} mis à jour.")
    sentry_sdk.capture_message(f"Client {client_id} mis à jour")

# Supprimer un client
def delete_client(db: Session, token: str, client_id: int):
    if not has_permission(token, 'delete_client'):
        print("❌ Permission refusée : delete_client")
        return
    client = db.query(Client).get(client_id)
    if not client:
        print(f"❌ Client ID {client_id} introuvable.")
        return
    db.delete(client)
    db.commit()
    print(f"✅ Client ID {client_id} supprimé.")
    sentry_sdk.capture_message(f"Client {client_id} supprimé")

# Mettre à jour un contrat
def update_contract(db: Session, token: str, contract_id: int, total_amount: float = None, amount_due: float = None, is_signed: bool = None):
    if not has_permission(token, 'update_contract'):
        print("❌ Permission refusée : update_contract")
        return
    contract = db.query(Contract).get(contract_id)
    if not contract:
        print(f"❌ Contrat ID {contract_id} introuvable.")
        return
    if total_amount is not None:
        contract.total_amount = total_amount
    if amount_due is not None:
        contract.amount_due = amount_due
    if is_signed is not None:
        contract.is_signed = is_signed
    db.commit()
    print(f"✅ Contrat ID {contract_id} mis à jour.")
    sentry_sdk.capture_message(f"Contrat {contract_id} mis à jour")

# Supprimer un contrat
def delete_contract(db: Session, token: str, contract_id: int):
    if not has_permission(token, 'delete_contract'):
        print("❌ Permission refusée : delete_contract")
        return
    contract = db.query(Contract).get(contract_id)
    if not contract:
        print(f"❌ Contrat ID {contract_id} introuvable.")
        return
    db.delete(contract)
    db.commit()
    print(f"✅ Contrat ID {contract_id} supprimé.")
    sentry_sdk.capture_message(f"Contrat {contract_id} supprimé")

# Mettre à jour un événement
def update_event(db: Session, token: str, event_id: int, support_email: str = None, start_date: str = None, end_date: str = None, location: str = None, attendees: int = None, notes: str = None):
    if not has_permission(token, 'update_event'):
        print("❌ Permission refusée : update_event")
        return
    event = db.query(Event).get(event_id)
    if not event:
        print(f"❌ Événement ID {event_id} introuvable.")
        return
    if support_email:
        support = db.query(User).filter_by(email=support_email).first()
        if not support:
            print(f"❌ Support '{support_email}' introuvable.")
            return
        event.support_id = support.id
    if start_date:
        event.start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
    if end_date:
        event.end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    if location:
        event.location = location
    if attendees is not None:
        event.attendees = attendees
    if notes is not None:
        event.notes = notes
    db.commit()
    print(f"✅ Événement ID {event_id} mis à jour.")
    sentry_sdk.capture_message(f"Événement {event_id} mis à jour")

# Supprimer un événement
def delete_event(db: Session, token: str, event_id: int):
    if not has_permission(token, 'delete_event'):
        print("❌ Permission refusée : delete_event")
        return
    event = db.query(Event).get(event_id)
    if not event:
        print(f"❌ Événement ID {event_id} introuvable.")
        return
    db.delete(event)
    db.commit()
    print(f"✅ Événement ID {event_id} supprimé.")
    sentry_sdk.capture_message(f"Événement {event_id} supprimé")