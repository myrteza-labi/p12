#!/usr/bin/env python3
# flake8: noqa: E402

import os
import sys

# Permet d'ajouter le dossier parent au PYTHONPATH pour trouver les modules du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import click
from sqlalchemy.orm import Session

from database.engine import engine
from services.auth import login as auth_login
from services.token import create_token, load_token, decode_token
from services.write import (
    create_user as svc_create_user,
    create_client as svc_create_client,
    create_contract as svc_create_contract,
    create_event as svc_create_event,
    update_user as svc_update_user,
    delete_user as svc_delete_user,
    update_client as svc_update_client,
    delete_client as svc_delete_client,
    update_contract as svc_update_contract,
    delete_contract as svc_delete_contract,
    update_event as svc_update_event,
    delete_event as svc_delete_event,
)
from services.read import (
    get_all_clients,
    get_all_contracts,
    get_all_events,
)
from rich.console import Console
from rich.table import Table
from models import Contract, User

console = Console()


@click.group()
def cli():
    """📦 Epic Events CRM - Interface en ligne de commande"""
    pass


# LOGIN
@click.command(name="login")
def login_cmd():
    """🔐 Se connecter et stocker un token JWT localement"""
    db = Session(bind=engine)
    email = click.prompt("Email")
    password = click.prompt("Mot de passe", hide_input=True)
    user = auth_login(db, email, password)
    if not user:
        console.print("❌ Identifiants incorrects.")
        return

    token = create_token(user.id, user.role.name)
    with open(".token", "w") as f:
        f.write(token)

    console.print("✅ Connexion réussie.")


# CREATE Commands
@click.command(name="create-user")
@click.option("--name", prompt=True)
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--role", prompt=True)
def create_user_cmd(name, email, password, role):
    """➕ Créer un nouveau collaborateur"""
    token = load_token()
    svc_create_user(Session(bind=engine), token, name, email, password, role)


@click.command(name="create-client")
@click.option("--full-name", prompt="Nom complet du client")
@click.option("--email", prompt="Email du client")
def create_client_cmd(full_name, email):
    """➕ Créer un nouveau client"""
    token = load_token()
    svc_create_client(Session(bind=engine), token, full_name, email)


@click.command(name="create-contract")
@click.option("--client-email", prompt="Email du client")
@click.option("--commercial-email", prompt="Email du commercial")
@click.option("--total-amount", prompt="Montant total", type=float)
@click.option("--amount-due", prompt="Montant restant dû", type=float)
@click.option("--is-signed", prompt="Contrat signé ? (True/False)", type=bool)
def create_contract_cmd(
    client_email, commercial_email, total_amount, amount_due, is_signed
):
    """➕ Créer un nouveau contrat"""
    token = load_token()
    svc_create_contract(
        Session(bind=engine),
        token,
        client_email,
        commercial_email,
        total_amount,
        amount_due,
        is_signed,
    )


@click.command(name="create-event")
@click.option("--contract-id", prompt="ID du contrat", type=int)
@click.option("--client-email", prompt="Email du client")
@click.option("--support-email", prompt="Email du support")
@click.option("--start-date", prompt="Date de début (YYYY-MM-DD HH:MM)")
@click.option("--end-date", prompt="Date de fin (YYYY-MM-DD HH:MM)")
@click.option("--location", prompt="Lieu")
@click.option("--attendees", prompt="Nombre de participants", type=int)
@click.option("--notes", prompt="Notes (optionnel)", default="", required=False)
def create_event_cmd(
    contract_id,
    client_email,
    support_email,
    start_date,
    end_date,
    location,
    attendees,
    notes,
):
    """📅 Créer un nouvel événement"""
    token = load_token()
    db = Session(bind=engine)

    contract = db.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        console.print(f"❌ Contrat avec l'ID {contract_id} introuvable.")
        return

    if not contract.is_signed:
        console.print("❌ Impossible de créer un événement : le contrat n'est pas signé.")
        return

    svc_create_event(
        db,
        token,
        contract_id,
        client_email,
        support_email,
        start_date,
        end_date,
        location,
        attendees,
        notes,
    )


# LIST Commands
@click.command(name="list-clients")
def list_clients_cmd():
    """📋 Lister tous les clients"""
    token = load_token()
    clients = get_all_clients(Session(bind=engine), token)

    table = Table(title="Clients")
    table.add_column("ID", justify="right")
    table.add_column("Nom")
    table.add_column("Email")

    for c in clients:
        table.add_row(str(c.id), c.full_name, c.email)

    console.print(table)


@click.command(name="list-contracts")
def list_contracts_cmd():
    """📋 Lister tous les contrats"""
    token = load_token()
    contracts = get_all_contracts(Session(bind=engine), token)

    table = Table(title="Contrats")
    table.add_column("ID", justify="right")
    table.add_column("Client")
    table.add_column("Montant")
    table.add_column("Signé")

    for ct in contracts:
        table.add_row(
            str(ct.id), ct.client.full_name, f"{ct.total_amount}", str(ct.is_signed)
        )

    console.print(table)


@click.command(name="list-events")
def list_events_cmd():
    """📋 Lister tous les événements"""
    token = load_token()
    events = get_all_events(Session(bind=engine), token)

    table = Table(title="Événements")
    table.add_column("ID", justify="right")
    table.add_column("Client")
    table.add_column("Support")
    table.add_column("Début")

    for ev in events:
        support_name = ev.support.name if ev.support else "-"
        table.add_row(
            str(ev.id),
            ev.client.full_name,
            support_name,
            ev.start_date.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


# UPDATE Commands
@click.command(name="update-user")
@click.option("--id", "user_id", prompt=True, type=int)
@click.option("--name", default=None)
@click.option("--email", default=None)
@click.option("--role", "role_name", default=None)
def update_user_cmd(user_id, name, email, role_name):
    """✏️ Mettre à jour un collaborateur"""
    token = load_token()
    svc_update_user(Session(bind=engine), token, user_id, name, email, role_name)


@click.command(name="update-client")
@click.option("--id", "client_id", prompt=True, type=int)
@click.option("--full-name", default=None)
@click.option("--email", default=None)
@click.option("--phone", default=None)
def update_client_cmd(client_id, full_name, email, phone):
    """✏️ Mettre à jour un client"""
    token = load_token()
    svc_update_client(Session(bind=engine), token, client_id, full_name, email, phone)


@click.command(name="update-contract")
@click.option("--id", "contract_id", prompt=True, type=int)
@click.option("--total-amount", default=None, type=float)
@click.option("--amount-due", default=None, type=float)
@click.option("--is-signed", default=None, type=bool)
def update_contract_cmd(contract_id, total_amount, amount_due, is_signed):
    """✏️ Mettre à jour un contrat"""
    token = load_token()
    svc_update_contract(
        Session(bind=engine), token, contract_id, total_amount, amount_due, is_signed
    )


@click.command(name="update-event")
@click.option("--id", "event_id", prompt=True, type=int)
@click.option("--support-email", default=None)
@click.option("--start-date", default=None)
@click.option("--end-date", default=None)
@click.option("--location", default=None)
@click.option("--attendees", default=None, type=int)
@click.option("--notes", default=None)
def update_event_cmd(
    event_id, support_email, start_date, end_date, location, attendees, notes
):
    """✏️ Mettre à jour un événement"""
    token = load_token()
    svc_update_event(
        Session(bind=engine),
        token,
        event_id,
        support_email,
        start_date,
        end_date,
        location,
        attendees,
        notes,
    )


# DELETE Commands
@click.command(name="delete-user")
@click.option("--id", "user_id", prompt=True, type=int)
def delete_user_cmd(user_id):
    """🗑️ Supprimer un collaborateur"""
    token = load_token()
    svc_delete_user(Session(bind=engine), token, user_id)


@click.command(name="delete-client")
@click.option("--id", "client_id", prompt=True, type=int)
def delete_client_cmd(client_id):
    """🗑️ Supprimer un client"""
    token = load_token()
    svc_delete_client(Session(bind=engine), token, client_id)


@click.command(name="delete-contract")
@click.option("--id", "contract_id", prompt=True, type=int)
def delete_contract_cmd(contract_id):
    """🗑️ Supprimer un contrat"""
    token = load_token()
    svc_delete_contract(Session(bind=engine), token, contract_id)


@click.command(name="delete-event")
@click.option("--id", "event_id", prompt=True, type=int)
def delete_event_cmd(event_id):
    """🗑️ Supprimer un événement"""
    token = load_token()
    svc_delete_event(Session(bind=engine), token, event_id)


@click.command(name="whoami")
def whoami_cmd():
    """🔍 Afficher l'utilisateur actuellement connecté"""
    token = load_token()
    if not token:
        console.print("❌ Vous n'êtes pas connecté.")
        return

    data = decode_token(token)
    if not data:
        console.print("❌ Jeton invalide ou expiré.")
        return

    db = Session(bind=engine)
    user = db.get(User, data["user_id"])
    console.print(f"🔎 Connecté : {user.email} (rôle : {data['role']})")


cli.add_command(login_cmd)
cli.add_command(create_user_cmd)
cli.add_command(create_client_cmd)
cli.add_command(create_contract_cmd)
cli.add_command(create_event_cmd)
cli.add_command(list_clients_cmd)
cli.add_command(list_contracts_cmd)
cli.add_command(list_events_cmd)
cli.add_command(update_user_cmd)
cli.add_command(update_client_cmd)
cli.add_command(update_contract_cmd)
cli.add_command(update_event_cmd)
cli.add_command(delete_user_cmd)
cli.add_command(delete_client_cmd)
cli.add_command(delete_contract_cmd)
cli.add_command(delete_event_cmd)
cli.add_command(whoami_cmd)


if __name__ == "__main__":
    cli()
