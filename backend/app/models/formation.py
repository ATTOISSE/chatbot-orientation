"""
Modèles Formation, Etablissement, Domaine - Base de données des formations
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


# Table d'association many-to-many pour Formation <-> Domaine
formation_domaine = Table(
    'formation_domaine',
    Base.metadata,
    Column('formation_id', Integer, ForeignKey('formations.id', ondelete='CASCADE')),
    Column('domaine_id', Integer, ForeignKey('domaines.id', ondelete='CASCADE'))
)


class Etablissement(Base):
    """Établissement d'enseignement supérieur"""
    __tablename__ = "etablissements"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(500), nullable=False, index=True)
    type_etablissement = Column(String(100), nullable=True)  # Public/Privé
    ville = Column(String(100), nullable=True, index=True)
    region = Column(String(100), nullable=True, index=True)
    adresse = Column(Text, nullable=True)
    telephone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    site_web = Column(String(500), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    formations = relationship("Formation", back_populates="etablissement")
    
    def __repr__(self):
        return f"<Etablissement(id={self.id}, nom={self.nom}, ville={self.ville})>"


class Domaine(Base):
    """Domaine d'études (Informatique, Santé, Droit, etc.)"""
    __tablename__ = "domaines"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('domaines.id'), nullable=True)  # Hiérarchie
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    formations = relationship("Formation", secondary=formation_domaine, back_populates="domaines")
    parent = relationship("Domaine", remote_side=[id], backref="sous_domaines")
    
    def __repr__(self):
        return f"<Domaine(id={self.id}, nom={self.nom})>"


class Formation(Base):
    """Formation académique"""
    __tablename__ = "formations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informations principales
    intitule = Column(String(500), nullable=False, index=True)
    diplome = Column(String(255), nullable=True, index=True)  # Licence, Master, DUT, etc.
    niveau = Column(String(100), nullable=True)  # Bac+3, Bac+5, etc.
    duree = Column(String(50), nullable=True)  # 3 ans, 2 ans, etc.
    
    # Établissement
    etablissement_id = Column(Integer, ForeignKey("etablissements.id", ondelete="CASCADE"), nullable=False)
    
    # Détails académiques
    conditions_admission = Column(Text, nullable=True)
    objectifs = Column(Text, nullable=True)
    debouches = Column(Text, nullable=True)
    
    # Coûts et financement
    cout_inscription = Column(Float, nullable=True)
    bourses_disponibles = Column(Boolean, default=False)
    
    # Accréditation
    est_accredite = Column(Boolean, default=False)
    organisme_accreditation = Column(String(255), nullable=True)  # ANAQ-Sup, etc.
    
    # Source des données
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    etablissement = relationship("Etablissement", back_populates="formations")
    domaines = relationship("Domaine", secondary=formation_domaine, back_populates="formations")
    data_source = relationship("DataSource", back_populates="formations")
    
    def __repr__(self):
        return f"<Formation(id={self.id}, intitule={self.intitule}, diplome={self.diplome})>"


class DataSource(Base):
    """Source des données (pour la traçabilité)"""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False, unique=True)
    type_source = Column(String(100), nullable=True)  # API, Scraping, Manuel, etc.
    url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    fiabilite = Column(Float, nullable=True)  # Score de fiabilité 0-1
    derniere_maj = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    formations = relationship("Formation", back_populates="data_source")
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, nom={self.nom}, type={self.type_source})>"
