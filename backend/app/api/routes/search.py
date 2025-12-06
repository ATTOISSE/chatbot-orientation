"""
COMMIT 7: Search Endpoints
Recherche sophistiquée de formations avec filtres avancés
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models.formation import Formation, Etablissement, Domaine
from app.schemas.search import (
    FormationSearchResponse,
    SearchFilters,
    SearchResults,
    FormationDetail
)
from app.core.pagination import PaginationParams, apply_pagination

router = APIRouter(prefix="/api/v1/search", tags=["search"])


class SearchService:
    """Service for sophisticated formation searches"""
    
    @staticmethod
    def build_search_query(db: Session, filters: SearchFilters):
        """Build database query with filters"""
        query = db.query(Formation)
        
        # Text search - name or description
        if filters.q:
            search_term = f"%{filters.q.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Formation.intitule).like(search_term),
                    func.lower(Formation.objectifs).like(search_term),
                    func.lower(Formation.conditions_admission).like(search_term)
                )
            )
        
        # Filter by domain
        if filters.domaine_id:
            query = query.filter(Formation.domaines.any(Domaine.id == filters.domaine_id))
        
        # Filter by domain name (wildcard)
        if filters.domaine:
            query = query.filter(
                Formation.domaines.any(
                    func.lower(Domaine.nom).like(f"%{filters.domaine.lower()}%")
                )
            )
        
        # Filter by establishment
        if filters.etablissement_id:
            query = query.filter(Formation.etablissement_id == filters.etablissement_id)
        
        # Filter by establishment name
        if filters.etablissement:
            query = query.filter(
                Formation.etablissement.has(
                    func.lower(Etablissement.nom).like(f"%{filters.etablissement.lower()}%")
                )
            )
        
        # Filter by city
        if filters.ville:
            query = query.filter(
                Formation.etablissement.has(
                    func.lower(Etablissement.ville).like(f"%{filters.ville.lower()}%")
                )
            )
        
        # Filter by niveau (L1, L2, L3, M1, M2, etc.)
        if filters.niveau:
            query = query.filter(Formation.niveau == filters.niveau)
        
        # Filter by diplome (Licence, Master, etc.)
        if filters.type_formation:
            query = query.filter(Formation.diplome == filters.type_formation)
        
        # Filter by cost range
        if filters.cost_min is not None:
            query = query.filter(Formation.cout_inscription >= filters.cost_min)
        
        if filters.cost_max is not None:
            query = query.filter(Formation.cout_inscription <= filters.cost_max)
        
        # Filter by debouches (opportunities/careers)
        if filters.debouches:
            search_term = f"%{filters.debouches.lower()}%"
            query = query.filter(
                func.lower(Formation.debouches).like(search_term)
            )
        
        # Filter by accreditation
        if filters.accredited_only:
            query = query.filter(Formation.est_accredite == True)
        
        return query


@router.post("/formations", response_model=SearchResults)
async def search_formations(
    filters: SearchFilters = None,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Search formations with advanced filters
    
    Filters:
    - q: Text search (name, description, objectives)
    - domaine_id: Filter by domain ID
    - domaine: Filter by domain name
    - etablissement_id: Filter by establishment ID
    - etablissement: Filter by establishment name
    - ville: Filter by city
    - type_formation: Filter by type (Licence, Master, etc.)
    - niveau: Filter by level (L1, L2, L3, M1, M2, etc.)
    - cost_min/cost_max: Filter by cost range
    - debut: Filter by start month
    - debouches: Filter by career opportunities
    
    Returns paginated results with metadata
    """
    
    if filters is None:
        filters = SearchFilters()
    
    # Build query
    query = SearchService.build_search_query(db, filters)
    
    # Count total before pagination
    total = query.count()
    
    # Apply sorting
    if filters.sort_by == "cost_asc":
        query = query.order_by(Formation.cout_inscription.asc())
    elif filters.sort_by == "cost_desc":
        query = query.order_by(Formation.cout_inscription.desc())
    elif filters.sort_by == "name":
        query = query.order_by(Formation.intitule.asc())
    elif filters.sort_by == "newest":
        query = query.order_by(Formation.created_at.desc())
    else:
        query = query.order_by(Formation.intitule.asc())
    
    # Apply pagination
    query, page_info = apply_pagination(query, pagination)
    
    # Execute query
    formations = query.all()
    
    # Build response
    return SearchResults(
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=page_info.total_pages,
        has_next=page_info.has_next,
        has_prev=page_info.has_prev,
        items=[FormationSearchResponse.from_orm(f) for f in formations]
    )


@router.get("/formations/{formation_id}", response_model=FormationDetail)
async def get_formation_detail(
    formation_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a formation"""
    
    formation = db.query(Formation).filter(
        Formation.id == formation_id
    ).first()
    
    if not formation:
        raise HTTPException(status_code=404, detail="Formation not found")
    
    return FormationDetail.from_orm(formation)


@router.get("/domaines", response_model=List[dict])
async def list_domaines(
    db: Session = Depends(get_db)
):
    """List all available domains with formation count"""
    
    try:
        domaines = db.query(
            Domaine.id,
            Domaine.nom,
            func.count(Formation.id).label("formations_count")
        ).outerjoin(Formation.domaines).group_by(Domaine.id, Domaine.nom).all()
        
        return [
            {
                "id": d[0],
                "nom": d[1],
                "formations_count": d[2] or 0
            }
            for d in domaines
        ]
    except Exception as e:
        # Fallback: simple domaines list
        domaines = db.query(Domaine).all()
        return [
            {
                "id": d.id,
                "nom": d.nom,
                "formations_count": len(d.formations)
            }
            for d in domaines
        ]


@router.get("/villes", response_model=List[dict])
async def list_villes(
    db: Session = Depends(get_db)
):
    """List all available cities with formation count"""
    
    villes = db.query(
        Etablissement.ville,
        func.count(Formation.id).label("formations_count")
    ).join(Formation).group_by(Etablissement.ville).all()
    
    return [
        {
            "ville": v[0],
            "formations_count": v[1]
        }
        for v in villes if v[0]
    ]


@router.get("/etablissements", response_model=List[dict])
async def list_etablissements(
    db: Session = Depends(get_db)
):
    """List all establishments with formation count"""
    
    etablissements = db.query(
        Etablissement.id,
        Etablissement.nom,
        Etablissement.ville,
        func.count(Formation.id).label("formations_count")
    ).outerjoin(Formation).group_by(
        Etablissement.id,
        Etablissement.nom,
        Etablissement.ville
    ).all()
    
    return [
        {
            "id": e[0],
            "nom": e[1],
            "ville": e[2],
            "formations_count": e[3] or 0
        }
        for e in etablissements
    ]


@router.get("/stats", response_model=dict)
async def get_search_stats(
    db: Session = Depends(get_db)
):
    """Get search statistics"""
    
    total_formations = db.query(func.count(Formation.id)).scalar() or 0
    total_domaines = db.query(func.count(Domaine.id)).scalar() or 0
    total_etablissements = db.query(func.count(Etablissement.id)).scalar() or 0
    
    # Cost statistics
    min_cost = db.query(func.min(Formation.cout_inscription)).scalar() or 0
    max_cost = db.query(func.max(Formation.cout_inscription)).scalar() or 0
    avg_cost = db.query(func.avg(Formation.cout_inscription)).scalar() or 0
    
    # Most common diploma types
    diplomes = db.query(
        Formation.diplome,
        func.count(Formation.id).label("count")
    ).group_by(Formation.diplome).order_by(func.count(Formation.id).desc()).limit(5).all()
    
    # Most common levels
    levels = db.query(
        Formation.niveau,
        func.count(Formation.id).label("count")
    ).group_by(Formation.niveau).order_by(func.count(Formation.id).desc()).limit(5).all()
    
    return {
        "total_formations": total_formations,
        "total_domaines": total_domaines,
        "total_etablissements": total_etablissements,
        "cost": {
            "min": float(min_cost) if min_cost else 0,
            "max": float(max_cost) if max_cost else 0,
            "avg": float(avg_cost) if avg_cost else 0
        },
        "common_diplomes": [{"type": d[0], "count": d[1]} for d in diplomes],
        "common_levels": [{"level": l[0], "count": l[1]} for l in levels]
    }
