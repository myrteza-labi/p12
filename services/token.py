import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Chargement des configurations
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES", 30))

# Définition des permissions par rôle
# Tous les rôles peuvent lire toutes les entités (view_all)
permissions = {
    "gestion": [
        # lecture
        "view_all", "view_all_clients", "view_all_contracts", "view_all_events",
        # utilisateurs
        "create_user", "update_user", "delete_user",
        # clients
        "create_client", "update_client", "delete_client",
        # contrats
        "create_contract", "update_contract", "delete_contract",
        # événements
        "create_event", "update_event", "delete_event",
        # assignation
        "assign_support"
    ],
    "commercial": [
        "view_all_clients", "view_all_contracts", "view_all_events",
        "view_own_contracts",
        "create_client", "edit_client",
        "create_contract",
        "create_event"
    ],
    "support": [
        "view_all_clients", "view_all_contracts", "view_all_events",
        "view_assigned_events",
        "update_event"
    ]
}

# Création d'un jeton JWT
def create_token(user_id: int, role_name: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    payload = {"user_id": user_id, "role": role_name, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Décodage du jeton JWT
def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        print("❌ Le jeton a expiré.")
    except jwt.InvalidTokenError:
        print("❌ Jeton invalide.")
    return None

# Lecture du jeton JWT depuis le fichier local
def load_token(path: str = ".token") -> str | None:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ Jeton introuvable.")
        return None

# Vérification d'autorisation
def has_permission(token: str, action: str) -> bool:
    data = decode_token(token)
    if not data:
        return False
    role = data.get("role")
    allowed = permissions.get(role, [])
    # toute action view_* est couverte par view_all
    if action.startswith("view_") and "view_all" in allowed:
        return True
    return action in allowed