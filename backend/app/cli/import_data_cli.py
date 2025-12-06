"""
Data import CLI command
Commande pour importer les données JSON dans la base de données
"""

import asyncio
import logging
from app.scripts.import_data import import_all_data
from app.database import SessionLocal

logger = logging.getLogger(__name__)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def import_data_command():
    """Commande d'import de données"""
    print("\n" + "="*60)
    print("🚀 COMMIT 6: Data Import")
    print("="*60 + "\n")
    
    try:
        results = import_all_data()
        
        print("\n" + "="*60)
        print("✅ DATA IMPORT COMPLETED")
        print("="*60)
        print(f"Formations imported:............ {results.get('formations', 0):>5}")
        print(f"Établissements imported:........ {results.get('etablissements', 0):>5}")
        print(f"ANAQ Accreditations imported:... {results.get('anaq_accreditations', 0):>5}")
        print("="*60 + "\n")
        
        total = sum(results.values())
        if total > 0:
            print(f"✅ Successfully imported {total} records!")
        else:
            print("⚠️  No records were imported. Check data files in datas/ directory")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}\n")
        logger.error(f"Import error: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(import_data_command())
