# tests/test_crud.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from services.auth import hash_password, verify_password
from services.token import create_token, has_permission
from services.write import create_client, create_contract, create_event
from services.read import get_all_clients, get_all_contracts, get_all_events
from models.role import Role
from models.user import User
from datetime import datetime

@pytest.fixture(scope="module")
def engine():
    # In-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture(scope="module")
def tokens(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    # Create roles
    gestion = Role(name="gestion")
    commercial = Role(name="commercial")
    support = Role(name="support")
    session.add_all([gestion, commercial, support])
    session.commit()

    # Create users
    admin = User(name="Admin", email="admin@test", password=hash_password("p12"), role_id=gestion.id)
    comm = User(name="Comm", email="comm@test", password=hash_password("p12"), role_id=commercial.id)
    supp = User(name="Supp", email="supp@test", password=hash_password("p12"), role_id=support.id)
    session.add_all([admin, comm, supp])
    session.commit()

    # Generate tokens
    admin_token = create_token(admin.id, "gestion")
    comm_token = create_token(comm.id, "commercial")
    supp_token = create_token(supp.id, "support")

    session.close()
    return {"admin": admin_token, "commercial": comm_token, "support": supp_token}

def test_hash_and_verify():
    pwd = "secret"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed)

def test_permissions(tokens):
    assert has_permission(tokens["admin"], "create_user")
    assert not has_permission(tokens["commercial"], "create_user")
    assert has_permission(tokens["support"], "update_event")

def test_crud_flow(db, tokens):
    # Client creation by commercial
    create_client(db, tokens["commercial"], "Client A", "a@test")
    clients = get_all_clients(db, tokens["commercial"])
    assert any(c.email == "a@test" for c in clients)

    # Contract creation (signed)
    create_contract(db, tokens["commercial"], "a@test", "comm@test", 1000.0, 200.0, True)
    contracts = get_all_contracts(db, tokens["commercial"])
    assert any(c.client.email == "a@test" and c.is_signed for c in contracts)

    # Event creation allowed on signed contract
    create_event(db, tokens["commercial"], contracts[0].id, "a@test", "supp@test",
                 "2025-06-01 10:00", "2025-06-01 12:00", "loc", 5, "")
    events = get_all_events(db, tokens["commercial"])
    assert any(e.contract_id == contracts[0].id for e in events)

    # Contract creation (not signed)
    create_contract(db, tokens["commercial"], "a@test", "comm@test", 500.0, 500.0, False)
    # Attempt to create event on unsigned contract should not insert
    create_event(db, tokens["commercial"], contracts[0].id + 1, "a@test", "supp@test",
                 "2025-06-02 10:00", "2025-06-02 12:00", "loc", 5, "")
    events_after = get_all_events(db, tokens["commercial"])
    # No new event for the unsigned contract
    assert all(e.contract_id != contracts[0].id + 1 for e in events_after)
