"""
COMMIT 6: Import des 2566 formations depuis merge.json
Importe les données réelles du projet depuis chatbot-orientation/datas/merge.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Etablissement, Formation, Domaine
from app.database import SessionLocal

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemin vers merge.json
DATA_DIR = Path(__file__).parent.parent.parent.parent / "datas"
MERGE_FILE = DATA_DIR / "merge.json"


def load_merge_data() -> List[Dict[str, Any]]:
    """Charge merge.json (2566 formations)"""
    logger.info(f"Chargement de {MERGE_FILE}")
    
    if not MERGE_FILE.exists():
        logger.error(f"✗ Fichier non trouvé: {MERGE_FILE}")
        return []
    
    try:
        with open(MERGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✓ {len(data)} formations chargées depuis merge.json")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"✗ Erreur JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"✗ Erreur: {e}")
        return []


def import_merge_data(db: Session) -> Dict[str, int]:
    """
    Importe les 2566 formations depuis merge.json
    
    Structure merge.json:
    {
        "adresse": "BP 5005, Dakar-Fann",
        "telephone": "+221 33 824 23 79",
        "email": "rhuadb@uadb.edu.sn",
        "etablissement": "Université Cheikh Anta Diop (UCAD)",
        "type": "Public",
        "ville": "Dakar",
        "description_ecole": "Grande université publique...",
        "formation": "Médecine",
        "description-formation": "La filière médecine forme...",
        "debouches": "Médecin généraliste, spécialiste...",
        "domaine": "Medecine",
        "cout": 0
    }
    """
    merge_data = load_merge_data()
    
    if not merge_data:
        logger.error("Aucune donnée à importer")
        return {"error": "No data"}
    
    stats = {
        "etablissements_created": 0,
        "domaines_created": 0, 
        "formations_created": 0,
        "formations_skipped": 0,
        "errors": 0
    }
    
    # Cache pour éviter les requêtes répétées
    etablissements_cache = {}
    domaines_cache = {}
    
    logger.info(f"Début de l'importation de {len(merge_data)} formations...")
    
    for idx, item in enumerate(merge_data, 1):
        try:
            # =============== 1. ÉTABLISSEMENT ===============
            etablissement_nom = item.get("etablissement", "").strip()
            if not etablissement_nom:
                logger.warning(f"Ligne {idx}: établissement manquant, ignorée")
                stats["errors"] += 1
                continue
            
            # Utiliser le cache ou créer/récupérer l'établissement
            if etablissement_nom not in etablissements_cache:
                etablissement = db.query(Etablissement).filter(
                    Etablissement.nom == etablissement_nom
                ).first()
                
                if not etablissement:
                    etablissement = Etablissement(
                        nom=etablissement_nom,
                        type_etablissement=item.get("type", "Public").strip(),
                        ville=item.get("ville", "").strip() or None,
                        adresse=item.get("adresse", "").strip() or None,
                        telephone=item.get("telephone", "").strip() or None,
                        email=item.get("email", "").strip() or None,
                    )
                    db.add(etablissement)
                    db.flush()
                    stats["etablissements_created"] += 1
                    logger.debug(f"✓ Établissement créé: {etablissement_nom}")
                
                etablissements_cache[etablissement_nom] = etablissement
            else:
                etablissement = etablissements_cache[etablissement_nom]
            
            # =============== 2. DOMAINE ===============
            domaine_nom = item.get("domaine", "").strip()
            if not domaine_nom:
                domaine_nom = "Non classé"
            
            if domaine_nom not in domaines_cache:
                domaine = db.query(Domaine).filter(
                    Domaine.nom == domaine_nom
                ).first()
                
                if not domaine:
                    domaine = Domaine(nom=domaine_nom)
                    db.add(domaine)
                    db.flush()
                    stats["domaines_created"] += 1
                    logger.debug(f"✓ Domaine créé: {domaine_nom}")
                
                domaines_cache[domaine_nom] = domaine
            else:
                domaine = domaines_cache[domaine_nom]
            
            # =============== 3. FORMATION ===============
            formation_intitule = item.get("formation", "").strip()
            if not formation_intitule:
                logger.warning(f"Ligne {idx}: intitulé de formation manquant, ignorée")
                stats["errors"] += 1
                continue
            
            # Vérifier si la formation existe déjà (même intitulé + même établissement)
            existing = db.query(Formation).filter(
                Formation.intitule == formation_intitule,
                Formation.etablissement_id == etablissement.id
            ).first()
            
            if existing:
                stats["formations_skipped"] += 1
                logger.debug(f"Formation déjà existante: {formation_intitule} @ {etablissement_nom}")
                continue
            
            # Créer la formation
            formation = Formation(
                intitule=formation_intitule,
                etablissement_id=etablissement.id,
                objectifs=item.get("description-formation", "").strip() or None,
                debouches=item.get("debouches", "").strip() or None,
                cout_inscription=float(item.get("cout", 0)) if item.get("cout") is not None else None,
            )
            
            formation.domaines.append(domaine)
            db.add(formation)
            stats["formations_created"] += 1
            
            # Commit par batch de 100 pour performance
            if idx % 100 == 0:
                db.commit()
                logger.info(f"Progression: {idx}/{len(merge_data)} entrées traitées "
                           f"({stats['formations_created']} formations créées)")
            
        except IntegrityError as e:
            logger.error(f"Ligne {idx} - Erreur d'intégrité: {e}")
            db.rollback()
            stats["errors"] += 1
        except Exception as e:
            logger.error(f"Ligne {idx} ({item.get('formation', 'Unknown')}): {e}")
            stats["errors"] += 1
    
    # Commit final
    db.commit()
    
    # Rapport final
    logger.info(f"""
╔════════════════════════════════════════════════════╗
║   RÉSULTATS DE L'IMPORTATION (merge.json)          ║
╠════════════════════════════════════════════════════╣
║ Établissements créés: {stats['etablissements_created']:>4}                      ║
║ Domaines créés:       {stats['domaines_created']:>4}                      ║
║ Formations créées:    {stats['formations_created']:>4}                      ║
║ Formations ignorées:  {stats['formations_skipped']:>4} (doublons)           ║
║ Erreurs:              {stats['errors']:>4}                      ║
╚════════════════════════════════════════════════════╝
    """)
    
    return stats


def import_anaq_accreditations(db: Session) -> Dict[str, int]:
    """
    Importe les accréditations ANAQ-Sup depuis anaq_accreditations.json (optionnel)
    Met à jour le champ est_accredite des formations existantes
    """
    anaq_file = DATA_DIR / "anaq_accreditations.json"
    
    if not anaq_file.exists():
        logger.warning("Fichier anaq_accreditations.json non trouvé, étape ignorée")
        return {"updated": 0, "not_found": 0, "errors": 0}
    
    try:
        with open(anaq_file, 'r', encoding='utf-8') as f:
            accreditations_data = json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des accréditations: {e}")
        return {"updated": 0, "not_found": 0, "errors": 0}
    
    stats = {"updated": 0, "not_found": 0, "errors": 0}
    
    for item in accreditations_data:
        try:
            # Trouver la formation par intitulé et établissement
            formation = db.query(Formation).join(Etablissement).filter(
                Formation.intitule.ilike(f"%{item['formation']}%"),
                Etablissement.nom.ilike(f"%{item['etablissement']}%")
            ).first()
            
            if formation:
                formation.est_accredite = True
                formation.organisme_accreditation = "ANAQ-Sup"
                stats["updated"] += 1
            else:
                stats["not_found"] += 1
                logger.debug(f"Formation non trouvée: {item['formation']} @ {item['etablissement']}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'import de l'accréditation: {e}")
            stats["errors"] += 1
    
    db.commit()
    logger.info(f"✓ Accréditations ANAQ: {stats['updated']} formations mises à jour")
    return stats


def import_all_data() -> Dict[str, Any]:
    """Point d'entrée principal: importe toutes les données depuis merge.json"""
    logger.info("╔════════════════════════════════════════════════════╗")
    logger.info("║  IMPORT DES DONNÉES EDUGUIDE SENEGAL               ║")
    logger.info("║  Source: merge.json (2566 formations)              ║")
    logger.info("╚════════════════════════════════════════════════════╝")
    
    db = SessionLocal()
    results = {}
    
    try:
        # 1. Importer merge.json (établissements + domaines + formations)
        logger.info("\n📥 Étape 1/2: Import de merge.json...")
        results["merge"] = import_merge_data(db)
        
        # 2. Importer les accréditations ANAQ (optionnel)
        logger.info("\n📥 Étape 2/2: Import des accréditations ANAQ-Sup...")
        results["accreditations"] = import_anaq_accreditations(db)
        
        logger.info("\n✅ IMPORTATION TERMINÉE AVEC SUCCÈS")
        
    except Exception as e:
        logger.error(f"❌ ERREUR GÉNÉRALE: {e}")
        db.rollback()
        results["error"] = str(e)
    finally:
        db.close()
    
    return results


if __name__ == "__main__":
    import_all_data()
