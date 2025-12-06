"""
COMMIT 6: CLI pour construire la base de données optimisée du chatbot
Commande: python -m app.cli.build_db_cli
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scripts.build_chatbot_database import build_eduguide_database


def main():
    """Construit la base de données EduGuide optimisée pour le chatbot"""
    print("\n" + "="*70)
    print("  🤖 EDUGUIDE SENEGAL - CONSTRUCTION BASE DE DONNÉES CHATBOT")
    print("  📊 Sources: merge.json + anaq_accreditations.json")
    print("="*70 + "\n")
    
    try:
        results = build_eduguide_database()
        
        if "error" in results:
            print(f"\n❌ ERREUR: {results['error']}")
            return 1
        
        print("\n" + "="*70)
        print("  ✅ BASE DE DONNÉES CRÉÉE AVEC SUCCÈS!")
        print("="*70)
        print(f"\n📈 Résumé:")
        print(f"   • Établissements: {results.get('etablissements_created', 0)}")
        print(f"   • Domaines: {results.get('domaines_created', 0)}")
        print(f"   • Formations: {results.get('formations_created', 0)}")
        print(f"   • Accréditations ANAQ: {results.get('anaq_accredited', 0)}")
        print(f"\n   ⚠️  Doublons ignorés: {results.get('formations_duplicates', 0)}")
        print(f"   ⚠️  Enregistrements invalides: {results.get('formations_invalid', 0)}")
        
        print(f"\n💡 La base de données est prête pour le chatbot!")
        print(f"   • Données nettoyées et normalisées")
        print(f"   • Optimisée pour la recherche RAG")
        print(f"   • Enrichie avec les accréditations officielles")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
