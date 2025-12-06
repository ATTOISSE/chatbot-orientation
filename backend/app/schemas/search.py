"""
Search schemas for COMMIT 7
"""

from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class SearchFilters(BaseModel):
    """Search filters for formation queries"""
    
    q: Optional[str] = None  # Text search
    domaine_id: Optional[int] = None
    domaine: Optional[str] = None
    etablissement_id: Optional[int] = None
    etablissement: Optional[str] = None
    ville: Optional[str] = None
    type_formation: Optional[str] = None  # Licence, Master, DUT, etc.
    niveau: Optional[str] = None  # L1, L2, L3, M1, M2, etc.
    cost_min: Optional[float] = None
    cost_max: Optional[float] = None
    debouches: Optional[str] = None
    accredited_only: Optional[bool] = False
    sort_by: Optional[str] = "name"  # name, cost_asc, cost_desc, newest
    
    class Config:
        schema_extra = {
            "example": {
                "q": "informatique",
                "ville": "Dakar",
                "cost_min": 0,
                "cost_max": 5000000,
                "sort_by": "cost_asc"
            }
        }


class FormationSearchResponse(BaseModel):
    """Formation in search results"""
    
    id: int
    intitule: str
    diplome: Optional[str]
    niveau: Optional[str]
    duree: Optional[str]
    cout_inscription: Optional[float]
    debouches: Optional[str]
    
    class Config:
        from_attributes = True


class FormationDetail(BaseModel):
    """Detailed formation information"""
    
    id: int
    intitule: str
    diplome: Optional[str]
    niveau: Optional[str]
    duree: Optional[str]
    objectifs: Optional[str]
    debouches: Optional[str]
    conditions_admission: Optional[str]
    cout_inscription: Optional[float]
    bourses_disponibles: Optional[bool]
    est_accredite: Optional[bool]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PageInfo(BaseModel):
    """Pagination information"""
    
    total_pages: int
    has_next: bool
    has_prev: bool


class SearchResults(BaseModel):
    """Search results with pagination"""
    
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    items: List[FormationSearchResponse]
