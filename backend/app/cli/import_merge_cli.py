"""
COMMIT 6: CLI pour l'importation des 2566 formations depuis merge.json
Commande: python -m app.cli.import_data_cli
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scripts.import_merge_data import import_all_data


def import_data_command():
    """Commande CLI pour importer les données depuis merge.json"""
    print("\n" + "="*60)
    print("  EDUGUIDE SENEGAL - IMPORT DES DONNÉES")
    print("  Source: merge.json (2566 formations réelles)")
    print("="*60 + "\n")
    
    try:
        results = import_all_data()
        
        print("\n" + "="*60)
        print("  RAPPORT D'IMPORTATION")
        print("="*60)
        
        if "merge" in results:
            merge_stats = results["merge"]
            print(f"\n📊 Statistiques merge.json:")
            print(f"   • Établissements créés: {merge_stats.get('etablissements_created', 0)}")
            print(f"   • Domaines créés: {merge_stats.get('domaines_created', 0)}")
            print(f"   • Formations créées: {merge_stats.get('formations_created', 0)}")
            print(f"   • Formations ignorées (doublons): {merge_stats.get('formations_skipped', 0)}")
            print(f"   • Erreurs: {merge_stats.get('errors', 0)}")
        
        if "accreditations" in results:
            accred_stats = results["accreditations"]
            print(f"\n🎓 Accréditations ANAQ-Sup:")
            print(f"   • Formations mises à jour: {accred_stats.get('updated', 0)}")
            print(f"   • Non trouvées: {accred_stats.get('not_found', 0)}")
        
        if "error" in results:
            print(f"\n❌ Erreur: {results['error']}")
            return 1
        
        print("\n✅ Import terminé avec succès!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = import_data_command()
    sys.exit(exit_code)
