"""
Data import API endpoints - COMMIT 6
Routes pour importer les 2566 formations depuis merge.json
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_superuser
from app.models import User
from app.scripts.import_merge_data import import_all_data
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/admin/data",
    tags=["admin", "data-import"],
    dependencies=[Depends(get_current_superuser)]
)


class ImportResponse(BaseModel):
    """Réponse d'import de données"""
    etablissements_created: int
    domaines_created: int
    formations_created: int
    formations_skipped: int
    errors: int
    message: str


@router.post("/import", response_model=ImportResponse)
async def import_data(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Importer les 2566 formations depuis merge.json
    
    ⚠️  Endpoint réservé aux administrateurs
    
    Returns:
        - etablissements_created: Établissements créés
        - domaines_created: Domaines créés
        - formations_created: Formations créées
        - formations_skipped: Formations ignorées (doublons)
        - errors: Erreurs rencontrées
    """
    try:
        results = import_all_data()
        
        if "error" in results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during import: {results['error']}"
            )
        
        merge_stats = results.get("merge", {})
        
        return ImportResponse(
            etablissements_created=merge_stats.get("etablissements_created", 0),
            domaines_created=merge_stats.get("domaines_created", 0),
            formations_created=merge_stats.get("formations_created", 0),
            formations_skipped=merge_stats.get("formations_skipped", 0),
            errors=merge_stats.get("errors", 0),
            message=f"Import terminé: {merge_stats.get('formations_created', 0)} formations créées"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during data import: {str(e)}"
        )


@router.get("/import-status")
async def get_import_status(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Obtenir les statistiques des données importées
    
    ⚠️  Endpoint réservé aux administrateurs
    """
    from app.models import Formation, Etablissement, Domaine
    
    formations_count = db.query(Formation).count()
    etablissements_count = db.query(Etablissement).count()
    domaines_count = db.query(Domaine).count()
    
    return {
        "formations_total": formations_count,
        "etablissements_total": etablissements_count,
        "domaines_total": domaines_count,
        "import_ready": formations_count > 0 and etablissements_count > 0,
        "expected_formations": 2566  # Nombre attendu depuis merge.json
    }
