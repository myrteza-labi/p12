from database.engine import engine
from models.base import Base

# 🔽 On importe tous les modèles pour que SQLAlchemy les détecte
from models import client, contract, event, user, role

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès.")
