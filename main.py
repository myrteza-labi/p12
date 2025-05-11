from database.engine import engine

if __name__ == "__main__":
    try:
        conn = engine.connect()
        print("✅ Connexion réussie à la base de données.")
        conn.close()
    except Exception as e:
        print("❌ Erreur de connexion :", e)
