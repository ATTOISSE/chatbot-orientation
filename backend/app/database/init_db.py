"""
Script d'initialisation de la base de données
Crée toutes les tables si elles n'existent pas
"""
from app.database.base import engine, Base
from app.models import (
    User, Conversation, Message,
    Formation, Etablissement, Domaine, DataSource,
    StudentProfile
)


def init_db():
    """Créer toutes les tables dans la base de données"""
    print("🔧 Création des tables de la base de données...")
    
    # Importer tous les modèles avant de créer les tables
    # Cela garantit que SQLAlchemy connaît toutes les relations
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tables créées avec succès!")
    print("\nTables créées:")
    print("  - users (utilisateurs)")
    print("  - conversations (historique chat)")
    print("  - messages (messages chat)")
    print("  - etablissements (établissements)")
    print("  - domaines (domaines d'études)")
    print("  - formations (formations)")
    print("  - data_sources (sources de données)")
    print("  - student_profiles (profils étudiants 6D)")
    print("  - formation_domaine (association many-to-many)")


if __name__ == "__main__":
    init_db()
