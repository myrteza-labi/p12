from database.engine import engine
from models.base import Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès.")
