"""
COMMIT 6: Création d'une base de données optimisée pour le chatbot EduGuide
À partir de merge.json (2566 formations) + anaq_accreditations.json

Ce script transforme les données brutes en une base PostgreSQL propre et optimisée:
- Nettoyage et normalisation des données
- Déduplication intelligente
- Enrichissement avec accréditations ANAQ-Sup
- Optimisation pour la recherche RAG
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Etablissement, Formation, Domaine
from app.database import SessionLocal

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins des fichiers sources
DATA_DIR = Path(__file__).parent.parent.parent / "datas"  # /app/datas dans Docker
MERGE_FILE = DATA_DIR / "merge.json"
ANAQ_FILE = DATA_DIR / "anaq_accreditations.json"


class DataCleaner:
    """Utilitaire pour nettoyer et normaliser les données"""
    
    @staticmethod
    def clean_string(text: Optional[str]) -> Optional[str]:
        """Nettoie une chaîne de caractères"""
        if not text or not isinstance(text, str):
            return None
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Supprimer les caractères invisibles
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text if text else None
    
    @staticmethod
    def normalize_phone(phone: Optional[str]) -> Optional[str]:
        """Normalise un numéro de téléphone sénégalais"""
        if not phone:
            return None
        
        # Extraire uniquement les chiffres et le +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Format standard: +221 XX XXX XX XX
        if phone.startswith('+221'):
            return phone
        elif phone.startswith('221'):
            return '+' + phone
        elif phone.startswith('33') or phone.startswith('77') or phone.startswith('70'):
            return '+221 ' + phone
        
        return phone if len(phone) >= 9 else None
    
    @staticmethod
    def normalize_email(email: Optional[str]) -> Optional[str]:
        """Normalise une adresse email"""
        if not email:
            return None
        
        email = email.lower().strip()
        
        # Validation basique
        if '@' in email and '.' in email.split('@')[1]:
            return email
        
        return None
    
    @staticmethod
    def extract_ville(ville: Optional[str]) -> Optional[str]:
        """Normalise le nom de ville"""
        if not ville:
            return None
        
        ville = ville.strip()
        
        # Corrections communes
        ville_map = {
            'dakar': 'Dakar',
            'thies': 'Thiès',
            'thies': 'Thiès',
            'saint-louis': 'Saint-Louis',
            'ziguinchor': 'Ziguinchor',
            'diamnadio': 'Diamniadio',
            'diamniadio': 'Diamniadio',
            'kaolack': 'Kaolack',
            'tambacounda': 'Tambacounda',
            'kolda': 'Kolda',
        }
        
        ville_lower = ville.lower()
        return ville_map.get(ville_lower, ville.title())
    
    @staticmethod
    def parse_cout(cout: Any) -> Optional[float]:
        """Parse le coût de formation"""
        if cout is None or cout == '':
            return None
        
        try:
            return float(cout)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def extract_niveau_diplome(intitule: str, description: str = '') -> tuple[Optional[str], Optional[str]]:
        """
        Extrait le niveau (Bac+X) et le diplôme (Licence, Master, etc.)
        à partir de l'intitulé et de la description
        """
        text = f"{intitule} {description}".lower()
        
        # Niveaux
        niveau = None
        if 'doctorat' in text or 'phd' in text:
            niveau = 'Bac+8'
        elif 'master' in text or 'm2' in text:
            niveau = 'Bac+5'
        elif 'licence' in text or 'bachelor' in text or 'l3' in text:
            niveau = 'Bac+3'
        elif 'dut' in text or 'bts' in text or 'deug' in text:
            niveau = 'Bac+2'
        
        # Diplômes
        diplome = None
        if 'doctorat' in text:
            diplome = 'Doctorat'
        elif 'master' in text:
            diplome = 'Master'
        elif 'licence professionnelle' in text:
            diplome = 'Licence Professionnelle'
        elif 'licence' in text or 'bachelor' in text:
            diplome = 'Licence'
        elif 'dut' in text:
            diplome = 'DUT'
        elif 'bts' in text:
            diplome = 'BTS'
        
        return niveau, diplome


class EduGuideDBBuilder:
    """Constructeur de la base de données EduGuide optimisée"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cleaner = DataCleaner()
        
        # Caches pour éviter les requêtes répétées
        self.etablissements_cache: Dict[str, Etablissement] = {}
        self.domaines_cache: Dict[str, Domaine] = {}
        
        # Statistiques
        self.stats = {
            "merge_records_processed": 0,
            "etablissements_created": 0,
            "domaines_created": 0,
            "formations_created": 0,
            "formations_duplicates": 0,
            "formations_invalid": 0,
            "anaq_accredited": 0,
            "anaq_not_found": 0,
        }
    
    def load_merge_data(self) -> List[Dict[str, Any]]:
        """Charge merge.json"""
        logger.info(f"📂 Chargement de {MERGE_FILE}")
        
        if not MERGE_FILE.exists():
            logger.error(f"❌ Fichier non trouvé: {MERGE_FILE}")
            return []
        
        try:
            with open(MERGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ {len(data)} enregistrements chargés")
            return data
        except Exception as e:
            logger.error(f"❌ Erreur de chargement: {e}")
            return []
    
    def load_anaq_data(self) -> List[Dict[str, Any]]:
        """Charge anaq_accreditations.json"""
        logger.info(f"📂 Chargement de {ANAQ_FILE}")
        
        if not ANAQ_FILE.exists():
            logger.warning(f"⚠️  Fichier non trouvé: {ANAQ_FILE}")
            return []
        
        try:
            with open(ANAQ_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ {len(data)} accréditations chargées")
            return data
        except Exception as e:
            logger.error(f"❌ Erreur de chargement: {e}")
            return []
    
    def get_or_create_etablissement(self, raw_data: Dict) -> Optional[Etablissement]:
        """Récupère ou crée un établissement"""
        nom = self.cleaner.clean_string(raw_data.get("etablissement"))
        
        if not nom:
            return None
        
        # Vérifier le cache
        if nom in self.etablissements_cache:
            return self.etablissements_cache[nom]
        
        # Chercher en base
        etablissement = self.db.query(Etablissement).filter(
            Etablissement.nom == nom
        ).first()
        
        if not etablissement:
            # Créer l'établissement
            etablissement = Etablissement(
                nom=nom,
                type_etablissement=self.cleaner.clean_string(raw_data.get("type")) or "Public",
                ville=self.cleaner.extract_ville(raw_data.get("ville")),
                adresse=self.cleaner.clean_string(raw_data.get("adresse")),
                telephone=self.cleaner.normalize_phone(raw_data.get("telephone")),
                email=self.cleaner.normalize_email(raw_data.get("email")),
            )
            self.db.add(etablissement)
            self.db.flush()
            self.stats["etablissements_created"] += 1
            logger.debug(f"✨ Établissement créé: {nom}")
        
        self.etablissements_cache[nom] = etablissement
        return etablissement
    
    def get_or_create_domaine(self, nom_domaine: str) -> Domaine:
        """Récupère ou crée un domaine"""
        nom = self.cleaner.clean_string(nom_domaine) or "Non classé"
        
        # Vérifier le cache
        if nom in self.domaines_cache:
            return self.domaines_cache[nom]
        
        # Chercher en base
        domaine = self.db.query(Domaine).filter(
            Domaine.nom == nom
        ).first()
        
        if not domaine:
            domaine = Domaine(nom=nom)
            self.db.add(domaine)
            self.db.flush()
            self.stats["domaines_created"] += 1
            logger.debug(f"✨ Domaine créé: {nom}")
        
        self.domaines_cache[nom] = domaine
        return domaine
    
    def is_duplicate_formation(self, intitule: str, etablissement_id: int) -> bool:
        """Vérifie si une formation existe déjà"""
        existing = self.db.query(Formation).filter(
            Formation.intitule == intitule,
            Formation.etablissement_id == etablissement_id
        ).first()
        
        return existing is not None
    
    def create_formation(self, raw_data: Dict, etablissement: Etablissement) -> Optional[Formation]:
        """Crée une formation depuis les données brutes"""
        intitule = self.cleaner.clean_string(raw_data.get("formation"))
        
        if not intitule:
            self.stats["formations_invalid"] += 1
            return None
        
        # Vérifier les doublons
        if self.is_duplicate_formation(intitule, etablissement.id):
            self.stats["formations_duplicates"] += 1
            logger.debug(f"⏭️  Formation dupliquée: {intitule} @ {etablissement.nom}")
            return None
        
        # Extraire niveau et diplôme
        description = self.cleaner.clean_string(raw_data.get("description-formation", ""))
        niveau, diplome = self.cleaner.extract_niveau_diplome(intitule, description or "")
        
        # Créer la formation
        formation = Formation(
            intitule=intitule,
            etablissement_id=etablissement.id,
            diplome=diplome,
            niveau=niveau,
            objectifs=description,
            debouches=self.cleaner.clean_string(raw_data.get("debouches")),
            cout_inscription=self.cleaner.parse_cout(raw_data.get("cout")),
        )
        
        # Ajouter le domaine
        domaine_nom = raw_data.get("domaine", "Non classé")
        domaine = self.get_or_create_domaine(domaine_nom)
        formation.domaines.append(domaine)
        
        self.db.add(formation)
        self.stats["formations_created"] += 1
        
        return formation
    
    def build_database_from_merge(self) -> bool:
        """Construit la base de données depuis merge.json"""
        logger.info("🏗️  ÉTAPE 1/2: Construction de la base depuis merge.json")
        
        merge_data = self.load_merge_data()
        if not merge_data:
            return False
        
        for idx, raw_record in enumerate(merge_data, 1):
            try:
                self.stats["merge_records_processed"] += 1
                
                # Créer/récupérer l'établissement
                etablissement = self.get_or_create_etablissement(raw_record)
                if not etablissement:
                    self.stats["formations_invalid"] += 1
                    continue
                
                # Créer la formation
                self.create_formation(raw_record, etablissement)
                
                # Commit par batch de 100
                if idx % 100 == 0:
                    self.db.commit()
                    logger.info(f"⏳ Progression: {idx}/{len(merge_data)} "
                               f"({self.stats['formations_created']} formations créées)")
            
            except Exception as e:
                logger.error(f"❌ Erreur ligne {idx}: {e}")
                self.db.rollback()
        
        self.db.commit()
        logger.info("✅ Importation merge.json terminée")
        return True
    
    def enrich_with_anaq(self) -> bool:
        """Enrichit la base avec les accréditations ANAQ-Sup"""
        logger.info("🎓 ÉTAPE 2/2: Enrichissement avec accréditations ANAQ-Sup")
        
        anaq_data = self.load_anaq_data()
        if not anaq_data:
            logger.warning("⚠️  Pas de données ANAQ à enrichir")
            return True
        
        for accred in anaq_data:
            try:
                etablissement_nom = self.cleaner.clean_string(accred.get("nom"))
                diplome_name = self.cleaner.clean_string(accred.get("diplome"))
                decision = accred.get("decision", "")
                
                if not etablissement_nom or not diplome_name:
                    continue
                
                # Recherche par similarité (ILIKE)
                formations = self.db.query(Formation).join(Etablissement).filter(
                    Etablissement.nom.ilike(f"%{etablissement_nom.split()[0]}%"),
                    Formation.intitule.ilike(f"%{diplome_name.split()[0]}%")
                ).all()
                
                for formation in formations:
                    if "accredited" in decision.lower():
                        formation.est_accredite = True
                        formation.organisme_accreditation = "ANAQ-Sup"
                        self.stats["anaq_accredited"] += 1
                
                if not formations:
                    self.stats["anaq_not_found"] += 1
            
            except Exception as e:
                logger.error(f"❌ Erreur ANAQ: {e}")
        
        self.db.commit()
        logger.info(f"✅ {self.stats['anaq_accredited']} formations accréditées")
        return True
    
    def print_statistics(self):
        """Affiche les statistiques finales"""
        logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║          STATISTIQUES DE CONSTRUCTION DE LA BDD          ║
╠══════════════════════════════════════════════════════════╣
║ 📊 Données sources:                                      ║
║    • Enregistrements merge.json: {self.stats['merge_records_processed']:>5}              ║
║                                                          ║
║ 🏫 Établissements:                                       ║
║    • Créés: {self.stats['etablissements_created']:>4}                                     ║
║                                                          ║
║ 📚 Domaines:                                             ║
║    • Créés: {self.stats['domaines_created']:>4}                                     ║
║                                                          ║
║ 🎓 Formations:                                           ║
║    • Créées: {self.stats['formations_created']:>4}                                    ║
║    • Doublons ignorés: {self.stats['formations_duplicates']:>4}                         ║
║    • Invalides: {self.stats['formations_invalid']:>4}                                ║
║                                                          ║
║ ✅ Accréditations ANAQ-Sup:                              ║
║    • Formations accréditées: {self.stats['anaq_accredited']:>4}                       ║
║    • Non trouvées: {self.stats['anaq_not_found']:>4}                               ║
╚══════════════════════════════════════════════════════════╝
        """)


def build_eduguide_database() -> Dict[str, Any]:
    """
    Point d'entrée principal: construit une base de données propre et optimisée
    pour le chatbot EduGuide Senegal
    """
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║     CONSTRUCTION BASE DE DONNÉES EDUGUIDE SENEGAL        ║")
    logger.info("║     Optimisée pour recherche RAG et chatbot              ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    
    db = SessionLocal()
    builder = EduGuideDBBuilder(db)
    
    try:
        # Étape 1: Construire depuis merge.json
        if not builder.build_database_from_merge():
            return {"error": "Failed to build from merge.json"}
        
        # Étape 2: Enrichir avec ANAQ
        builder.enrich_with_anaq()
        
        # Afficher les statistiques
        builder.print_statistics()
        
        return builder.stats
        
    except Exception as e:
        logger.error(f"❌ ERREUR FATALE: {e}")
        db.rollback()
        return {"error": str(e)}
    
    finally:
        db.close()


if __name__ == "__main__":
    build_eduguide_database()
