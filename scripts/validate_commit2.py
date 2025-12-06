#!/usr/bin/env python3
"""
Script de validation pour COMMIT 2
Vérifie que la configuration et les dépendances sont correctement installées
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

def check_config_import():
    """Vérifie que config.py peut être importé"""
    try:
        # Ajouter le backend au path
        backend_path = Path(__file__).parent.parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from app.config import Settings, get_settings
        print_success("config.py peut être importé")
        
        # Tester l'instanciation
        settings = get_settings()
        print_success(f"Settings instancié: {settings.APP_NAME}")
        
        # Vérifier les attributs critiques
        critical_attrs = [
            'APP_NAME', 'DATABASE_URL', 'JWT_SECRET', 
            'HUGGINGFACE_API_KEY', 'CHROMADB_HOST'
        ]
        
        missing = []
        for attr in critical_attrs:
            if not hasattr(settings, attr):
                missing.append(attr)
        
        if missing:
            print_error(f"Attributs manquants dans Settings: {', '.join(missing)}")
            return False
        else:
            print_success(f"Tous les attributs critiques présents ({len(critical_attrs)})")
            return True
            
    except ImportError as e:
        print_error(f"Impossible d'importer config.py: {e}")
        print_warning("Installez d'abord les dépendances: pip install -r backend/requirements.txt")
        return False
    except Exception as e:
        print_error(f"Erreur lors de l'import: {e}")
        return False

def check_requirements_content(filepath, expected_packages):
    """Vérifie que requirements.txt contient les packages attendus"""
    try:
        content = Path(filepath).read_text().lower()
        missing = []
        found = []
        
        for package in expected_packages:
            if package.lower() in content:
                found.append(package)
            else:
                missing.append(package)
        
        if missing:
            print_warning(f"Packages manquants dans {filepath}: {', '.join(missing)}")
            return False
        else:
            print_success(f"Tous les packages requis présents dans {filepath} ({len(found)})")
            return True
    except Exception as e:
        print_error(f"Erreur lecture {filepath}: {e}")
        return False

def check_docker_compose():
    """Vérifie docker-compose.yml"""
    try:
        content = Path("docker-compose.yml").read_text().lower()
        
        required_services = ['postgres', 'chromadb', 'backend', 'frontend']
        missing_services = []
        
        for service in required_services:
            if service in content:
                print_success(f"Service '{service}' trouvé dans docker-compose.yml")
            else:
                missing_services.append(service)
                print_error(f"Service '{service}' manquant dans docker-compose.yml")
        
        # Vérifier volumes
        if 'volumes:' in content and 'postgres_data' in content and 'chromadb_data' in content:
            print_success("Volumes configurés (postgres_data, chromadb_data)")
        else:
            print_warning("Volumes manquants ou incomplets")
        
        # Vérifier networks
        if 'networks:' in content and 'eduguide-network' in content:
            print_success("Network configuré (eduguide-network)")
        else:
            print_warning("Network manquant")
        
        return len(missing_services) == 0
        
    except Exception as e:
        print_error(f"Erreur lecture docker-compose.yml: {e}")
        return False

def check_dockerfile(filepath, expected_port, service_name):
    """Vérifie un Dockerfile"""
    try:
        content = Path(filepath).read_text()
        
        checks = {
            'Python 3.11': 'python:3.11' in content.lower(),
            f'Port {expected_port}': str(expected_port) in content,
            'WORKDIR': 'WORKDIR' in content,
            'CMD': 'CMD' in content
        }
        
        all_ok = True
        for check_name, result in checks.items():
            if result:
                print_success(f"{service_name} Dockerfile - {check_name} ✓")
            else:
                print_error(f"{service_name} Dockerfile - {check_name} manquant")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_error(f"Erreur lecture {filepath}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print(f"{BLUE}🔍 VALIDATION COMMIT 2 - Configuration & Dependencies{RESET}")
    print("="*60 + "\n")
    
    # Changer vers le dossier du projet
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print_info(f"Répertoire: {project_root}\n")
    
    results = []
    
    # 1. Vérifier les fichiers essentiels
    print(f"\n{BLUE}📁 Vérification des fichiers...{RESET}")
    files_to_check = [
        ("backend/app/config.py", "Configuration Pydantic"),
        ("backend/requirements.txt", "Dépendances backend"),
        ("frontend/requirements.txt", "Dépendances frontend"),
        ("backend/Dockerfile", "Dockerfile backend"),
        ("frontend/Dockerfile", "Dockerfile frontend"),
        ("docker-compose.yml", "Docker Compose"),
        (".env.example", "Template variables d'environnement"),
        ("COMMIT_2.md", "Documentation COMMIT 2")
    ]
    
    for filepath, description in files_to_check:
        results.append(check_file_exists(filepath, description))
    
    # 2. Vérifier le contenu de requirements.txt
    print(f"\n{BLUE}📦 Vérification des dépendances...{RESET}")
    
    backend_packages = ['fastapi', 'sqlalchemy', 'langchain', 'chromadb', 'uvicorn', 
                        'pydantic', 'python-jose', 'passlib']
    results.append(check_requirements_content(
        "backend/requirements.txt", 
        backend_packages
    ))
    
    frontend_packages = ['streamlit', 'plotly', 'pandas', 'httpx']
    results.append(check_requirements_content(
        "frontend/requirements.txt", 
        frontend_packages
    ))
    
    # 3. Vérifier docker-compose.yml
    print(f"\n{BLUE}🐳 Vérification Docker Compose...{RESET}")
    results.append(check_docker_compose())
    
    # 4. Vérifier les Dockerfiles
    print(f"\n{BLUE}🐳 Vérification Dockerfiles...{RESET}")
    results.append(check_dockerfile("backend/Dockerfile", 8000, "Backend"))
    results.append(check_dockerfile("frontend/Dockerfile", 8501, "Frontend"))
    
    # 5. Vérifier l'import de config.py
    print(f"\n{BLUE}⚙️  Vérification configuration Python...{RESET}")
    results.append(check_config_import())
    
    # Résumé final
    print("\n" + "="*60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    if failed == 0:
        print(f"{GREEN}✅ VALIDATION RÉUSSIE: {passed}/{total} vérifications passées{RESET}")
        print(f"{GREEN}🎉 COMMIT 2 est correctement configuré!{RESET}")
        print("\n📋 Prochaines étapes:")
        print("  1. Installer les dépendances: pip install -r backend/requirements.txt")
        print("  2. Créer le fichier .env à partir de .env.example")
        print("  3. Tester Docker: docker-compose config")
        print("  4. Passer au COMMIT 3: Modèles SQLAlchemy")
        return 0
    else:
        print(f"{RED}❌ VALIDATION ÉCHOUÉE: {failed}/{total} erreurs détectées{RESET}")
        print(f"{YELLOW}⚠️  Corrigez les erreurs ci-dessus avant de continuer{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
