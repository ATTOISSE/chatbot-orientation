"""
COMMIT 6: Data Import Scripts
Scripts pour importer les données JSON dans PostgreSQL
"""

import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Formation, Etablissement, Domaine
from app.database import SessionLocal
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ==================== DATA DIRECTORIES ====================
DATA_DIR = Path(__file__).parent.parent.parent / "datas"
FORMATIONS_FILE = DATA_DIR / "formations.json"
ECOLES_FILE = DATA_DIR / "ecoles.json"
ANAQ_FILE = DATA_DIR / "anaq_accreditations.json"


def load_json_file(filepath: Path) -> list:
    """Charger un fichier JSON"""
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} records from {filepath.name}")
        return data if isinstance(data, list) else [data]
    except Exception as e:
        logger.error(f"Error loading {filepath.name}: {e}")
        return []


def import_formations(db: Session) -> int:
    """Importer les formations depuis formations.json"""
    formations_data = load_json_file(FORMATIONS_FILE)
    
    if not formations_data:
        logger.info("No formations data to import")
        return 0
    
    imported = 0
    for item in formations_data:
        try:
            # Vérifier si la formation existe déjà
            existing = db.query(Formation).filter(
                Formation.intitule == item.get("intitule")
            ).first()
            
            if existing:
                logger.debug(f"Formation already exists: {item.get('intitule')}")
                continue
            
            # Créer la nouvelle formation
            formation = Formation(
                intitule=item.get("intitule", ""),
                diplome=item.get("diplome", ""),
                domaine=item.get("domaine", ""),
                etablissement=item.get("etablissement", ""),
                duree_annees=item.get("duree_annees", 3),
                type_formation=item.get("type_formation", ""),
                description=item.get("description", ""),
                conditions=item.get("conditions", ""),
                debouches=item.get("debouches", ""),
                source=item.get("source", "anaq"),
                external_id=item.get("id", "")
            )
            
            db.add(formation)
            imported += 1
            
        except Exception as e:
            logger.error(f"Error importing formation {item.get('intitule')}: {e}")
            continue
    
    try:
        db.commit()
        logger.info(f"Successfully imported {imported} formations")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing formations: {e}")
        imported = 0
    
    return imported


def import_etablissements(db: Session) -> int:
    """Importer les établissements depuis ecoles.json"""
    ecoles_data = load_json_file(ECOLES_FILE)
    
    if not ecoles_data:
        logger.info("No écoles data to import")
        return 0
    
    imported = 0
    for item in ecoles_data:
        try:
            # Vérifier si l'établissement existe déjà
            existing = db.query(Etablissement).filter(
                Etablissement.nom == item.get("nom")
            ).first()
            
            if existing:
                logger.debug(f"Établissement already exists: {item.get('nom')}")
                continue
            
            # Créer le nouvel établissement
            etablissement = Etablissement(
                nom=item.get("nom", ""),
                type_etablissement=item.get("type", ""),
                adresse=item.get("adresse", ""),
                ville=item.get("ville", ""),
                region=item.get("region", ""),
                telephone=item.get("telephone", ""),
                email=item.get("email", ""),
                website=item.get("website", ""),
                directeur=item.get("directeur", ""),
                description=item.get("description", ""),
                capacite=item.get("capacite", 0),
                annee_creation=item.get("annee_creation", 0),
                public_prive=item.get("public_prive", "public"),
                externe_id=item.get("id", "")
            )
            
            db.add(etablissement)
            imported += 1
            
        except Exception as e:
            logger.error(f"Error importing établissement {item.get('nom')}: {e}")
            continue
    
    try:
        db.commit()
        logger.info(f"Successfully imported {imported} établissements")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing établissements: {e}")
        imported = 0
    
    return imported


def import_anaq_accreditations(db: Session) -> int:
    """Importer les accréditations ANAQ depuis anaq_accreditations.json"""
    anaq_data = load_json_file(ANAQ_FILE)
    
    if not anaq_data:
        logger.info("No ANAQ data to import")
        return 0
    
    imported = 0
    for item in anaq_data:
        try:
            # Créer une formation pour chaque accréditation ANAQ
            # car ANAQ représente des formations accréditées
            existing = db.query(Formation).filter(
                Formation.external_id == item.get("id", ""),
                Formation.source == "anaq"
            ).first()
            
            if existing:
                logger.debug(f"ANAQ accreditation already exists: {item.get('code')}")
                continue
            
            formation = Formation(
                intitule=item.get("libelle", ""),
                diplome=item.get("libelle_diplome", ""),
                domaine=item.get("domaine", ""),
                etablissement=item.get("libelle_etablissement", ""),
                type_formation=item.get("niveau", ""),
                description=f"ANAQ Code: {item.get('code', '')}",
                source="anaq",
                external_id=item.get("id", ""),
                # Champs ANAQ spécifiques
                duree_annees=item.get("duree", 3)
            )
            
            db.add(formation)
            imported += 1
            
        except Exception as e:
            logger.error(f"Error importing ANAQ accreditation: {e}")
            continue
    
    try:
        db.commit()
        logger.info(f"Successfully imported {imported} ANAQ accreditations")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing ANAQ accreditations: {e}")
        imported = 0
    
    return imported


def import_all_data() -> dict:
    """Importer toutes les données"""
    logger.info("Starting data import process...")
    
    db = SessionLocal()
    results = {}
    
    try:
        # Importer les données
        results["formations"] = import_formations(db)
        results["etablissements"] = import_etablissements(db)
        results["anaq_accreditations"] = import_anaq_accreditations(db)
        
        total = sum(results.values())
        logger.info(f"Data import completed. Total records imported: {total}")
        
    finally:
        db.close()
    
    return results


if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Lancer l'import
    results = import_all_data()
    
    # Afficher les résultats
    print("\n" + "="*60)
    print("DATA IMPORT RESULTS")
    print("="*60)
    for key, count in results.items():
        print(f"{key:.<40} {count:>5} records")
    print("="*60 + "\n")
