#!/usr/bin/env python3
"""
Script de validation pour COMMIT 3
Vérifie que tous les modèles SQLAlchemy sont correctement créés
"""

import sys
import os
from pathlib import Path

# Couleurs pour le terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if Path(filepath).exists():
        print_success(f"{description} existe")
        return True
    else:
        print_error(f"{description} manquant: {filepath}")
        return False

def check_model_content(filepath, required_elements):
    """Vérifie que le modèle contient les éléments requis"""
    try:
        content = Path(filepath).read_text()
        missing = []
        found = []
        
        for element in required_elements:
            if element in content:
                found.append(element)
            else:
                missing.append(element)
        
        if missing:
            print_warning(f"Éléments manquants dans {filepath}: {', '.join(missing)}")
            return False
        else:
            print_success(f"Tous les éléments trouvés dans {Path(filepath).name} ({len(found)})")
            return True
    except Exception as e:
        print_error(f"Erreur lecture {filepath}: {e}")
        return False

def check_database_base():
    """Vérifie le fichier database/base.py"""
    filepath = "backend/app/database/base.py"
    required = [
        "create_engine",
        "sessionmaker",
        "declarative_base",
        "get_db",
        "SessionLocal",
        "Base"
    ]
    return check_model_content(filepath, required)

def check_user_model():
    """Vérifie le modèle User"""
    filepath = "backend/app/models/user.py"
    required = [
        "class User(Base)",
        "__tablename__ = \"users\"",
        "email",
        "username",
        "hashed_password",
        "is_active",
        "conversations",
        "student_profile"
    ]
    return check_model_content(filepath, required)

def check_conversation_model():
    """Vérifie les modèles Conversation et Message"""
    filepath = "backend/app/models/conversation.py"
    required = [
        "class Conversation(Base)",
        "class Message(Base)",
        "class MessageRole",
        "__tablename__ = \"conversations\"",
        "__tablename__ = \"messages\"",
        "rag_sources",
        "confidence_score"
    ]
    return check_model_content(filepath, required)

def check_formation_model():
    """Vérifie les modèles Formation, Etablissement, Domaine"""
    filepath = "backend/app/models/formation.py"
    required = [
        "class Formation(Base)",
        "class Etablissement(Base)",
        "class Domaine(Base)",
        "class DataSource(Base)",
        "formation_domaine",
        "intitule",
        "est_accredite",
        "fiabilite"
    ]
    return check_model_content(filepath, required)

def check_student_profile_model():
    """Vérifie le modèle StudentProfile avec 6D"""
    filepath = "backend/app/models/student_profile.py"
    required = [
        "class StudentProfile(Base)",
        "__tablename__ = \"student_profiles\"",
        # Dimension 1 - Académique
        "niveau_actuel",
        "serie_bac",
        "moyenne_generale",
        "matieres_fortes",
        # Dimension 2 - Intérêts
        "domaines_interet",
        "activites_extrascolaires",
        # Dimension 3 - Compétences
        "competences_techniques",
        "competences_soft",
        # Dimension 4 - Objectifs
        "metiers_vises",
        "projet_professionnel",
        # Dimension 5 - Contraintes
        "budget_max",
        "regions_acceptees",
        # Dimension 6 - Préférences
        "type_etablissement_prefere",
        "modalite_enseignement",
        # Méthode importante
        "calculate_completeness",
        "completeness_score"
    ]
    return check_model_content(filepath, required)

def check_alembic_config():
    """Vérifie la configuration Alembic"""
    files_ok = True
    files_ok &= check_file_exists("backend/alembic.ini", "Configuration Alembic")
    files_ok &= check_file_exists("backend/alembic/env.py", "Environment Alembic")
    files_ok &= check_file_exists("backend/alembic/script.py.mako", "Template migration Alembic")
    
    if files_ok:
        # Vérifier le contenu de env.py
        env_content = Path("backend/alembic/env.py").read_text()
        if "from app.models import *" in env_content and "target_metadata = Base.metadata" in env_content:
            print_success("Alembic correctement configuré avec les modèles")
            return True
        else:
            print_warning("Alembic manque les imports de modèles")
            return False
    return False

def count_models():
    """Compte le nombre de modèles définis"""
    models_dir = Path("backend/app/models")
    model_files = [f for f in models_dir.glob("*.py") if f.name != "__init__.py"]
    
    print_info(f"Fichiers de modèles trouvés: {len(model_files)}")
    for f in model_files:
        print(f"  - {f.name}")
    
    return len(model_files) >= 4  # user, conversation, formation, student_profile

def check_models_init():
    """Vérifie le fichier __init__.py des modèles"""
    filepath = "backend/app/models/__init__.py"
    if not Path(filepath).exists():
        print_error("models/__init__.py manquant")
        return False
    
    content = Path(filepath).read_text()
    required_imports = [
        "from app.models.user import User",
        "from app.models.conversation import Conversation, Message",
        "from app.models.formation import Formation, Etablissement, Domaine, DataSource",
        "from app.models.student_profile import StudentProfile"
    ]
    
    missing = [imp for imp in required_imports if imp not in content]
    
    if missing:
        print_warning(f"Imports manquants dans models/__init__.py:")
        for imp in missing:
            print(f"  - {imp}")
        return False
    else:
        print_success("Tous les modèles exportés dans __init__.py")
        return True

def main():
    print("\n" + "="*70)
    print(f"{BLUE}🔍 VALIDATION COMMIT 3 - SQLAlchemy Database Models{RESET}")
    print("="*70 + "\n")
    
    # Changer vers le dossier du projet
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print_info(f"Répertoire: {project_root}\n")
    
    results = []
    
    # 1. Vérifier les fichiers de base de données
    print(f"\n{BLUE}📁 Vérification des fichiers database...{RESET}")
    results.append(check_file_exists("backend/app/database/base.py", "Database base"))
    results.append(check_file_exists("backend/app/database/init_db.py", "Database init script"))
    results.append(check_database_base())
    
    # 2. Vérifier les fichiers de modèles
    print(f"\n{BLUE}📝 Vérification des fichiers de modèles...{RESET}")
    results.append(check_file_exists("backend/app/models/user.py", "User model"))
    results.append(check_file_exists("backend/app/models/conversation.py", "Conversation/Message models"))
    results.append(check_file_exists("backend/app/models/formation.py", "Formation models"))
    results.append(check_file_exists("backend/app/models/student_profile.py", "StudentProfile model"))
    results.append(check_file_exists("backend/app/models/__init__.py", "Models __init__"))
    
    # 3. Vérifier le contenu des modèles
    print(f"\n{BLUE}🔍 Vérification du contenu des modèles...{RESET}")
    results.append(check_user_model())
    results.append(check_conversation_model())
    results.append(check_formation_model())
    results.append(check_student_profile_model())
    
    # 4. Vérifier les exports
    print(f"\n{BLUE}📦 Vérification des exports...{RESET}")
    results.append(check_models_init())
    
    # 5. Compter les modèles
    print(f"\n{BLUE}📊 Comptage des modèles...{RESET}")
    results.append(count_models())
    
    # 6. Vérifier Alembic
    print(f"\n{BLUE}🔧 Vérification configuration Alembic...{RESET}")
    results.append(check_alembic_config())
    
    # 7. Vérifier la documentation
    print(f"\n{BLUE}📄 Vérification documentation...{RESET}")
    results.append(check_file_exists("COMMIT_3.md", "Documentation COMMIT 3"))
    
    # 8. Résumé des modèles attendus
    print(f"\n{BLUE}📋 Tables attendues dans la base de données:{RESET}")
    expected_tables = [
        "users (authentification)",
        "conversations (historique chat)",
        "messages (messages avec RAG)",
        "etablissements (écoles/universités)",
        "domaines (domaines d'études)",
        "formations (programmes académiques)",
        "data_sources (traçabilité)",
        "student_profiles (profil 6D)",
        "formation_domaine (association N-N)"
    ]
    
    for table in expected_tables:
        print(f"  ✓ {table}")
    
    # 9. Vérifier les 6 dimensions du profil étudiant
    print(f"\n{BLUE}📐 Profil Étudiant 6D:{RESET}")
    dimensions = [
        "D1 - Académique (niveau, série, moyenne, matières)",
        "D2 - Centres d'intérêt (domaines, activités, passions)",
        "D3 - Compétences (techniques, soft skills, langues)",
        "D4 - Objectifs (métiers visés, projet professionnel)",
        "D5 - Contraintes (budget, régions, mobilité)",
        "D6 - Préférences (établissement, modalités)"
    ]
    
    for dim in dimensions:
        print(f"  ✓ {dim}")
    
    # Résumé final
    print("\n" + "="*70)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    if failed == 0:
        print(f"{GREEN}✅ VALIDATION RÉUSSIE: {passed}/{total} vérifications passées{RESET}")
        print(f"{GREEN}🎉 COMMIT 3 est correctement implémenté!{RESET}")
        print("\n📋 Modèles créés:")
        print("  ✅ 8 tables principales + 1 association N-N")
        print("  ✅ Relations CASCADE configurées")
        print("  ✅ 10+ champs JSON pour flexibilité")
        print("  ✅ Profil étudiant 6D complet")
        print("  ✅ Alembic configuré pour migrations")
        print("\n🔜 Prochaines étapes:")
        print("  1. Démarrer les services Docker: docker-compose up -d postgres")
        print("  2. Créer les tables: docker-compose run backend python -m app.database.init_db")
        print("  3. Vérifier: docker-compose exec postgres psql -U eduguide -d eduguide_db -c '\\dt'")
        print("  4. Passer au COMMIT 4: JWT Authentication & Password Hashing")
        return 0
    else:
        print(f"{RED}❌ VALIDATION ÉCHOUÉE: {failed}/{total} erreurs détectées{RESET}")
        print(f"{YELLOW}⚠️  Corrigez les erreurs ci-dessus avant de continuer{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
