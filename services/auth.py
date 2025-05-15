from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.user import User


# Contexte pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Vérifier si un mot de passe correspond au hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Récupérer un utilisateur par email

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Fonction de login

def login(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
