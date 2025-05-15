# config.py
from dotenv import load_dotenv
import os

load_dotenv()  # lit .env à la racine

# URL de connexion à la BDD  
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/epicevents.db")

# Clé secrète pour JWT  
SECRET_KEY = os.getenv("SECRET_KEY", "change_me")

# DSN pour Sentry  
SENTRY_DSN = os.getenv("SENTRY_DSN", None)

# Options spécifiques à SQLAlchemy (SQLite)
SQLITE_CONNECT_ARGS = {"check_same_thread": False}

# Durée d'expiration du token (en minutes)
TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES", 30))
