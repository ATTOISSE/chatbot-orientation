"""
Modèle StudentProfile - Profil étudiant 6D
Les 6 dimensions: Académique, Intérêts, Compétences, Objectifs, Contraintes, Préférences
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class StudentProfile(Base):
    """Profil étudiant avec les 6 dimensions pour recommandations personnalisées"""
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Dimension 1: Académique
    niveau_actuel = Column(String(100), nullable=True)  # Terminale, Bac, Licence 1, etc.
    serie_bac = Column(String(50), nullable=True)  # S, L, G, etc.
    moyenne_generale = Column(Float, nullable=True)  # Note moyenne
    matieres_fortes = Column(JSON, nullable=True)  # Liste des matières fortes
    matieres_faibles = Column(JSON, nullable=True)  # Liste des matières faibles
    
    # Dimension 2: Centres d'intérêt
    domaines_interet = Column(JSON, nullable=True)  # Liste des domaines d'intérêt
    activites_extrascolaires = Column(JSON, nullable=True)  # Sports, clubs, etc.
    passions = Column(Text, nullable=True)  # Description libre
    
    # Dimension 3: Compétences et aptitudes
    competences_techniques = Column(JSON, nullable=True)  # Informatique, langues, etc.
    competences_soft = Column(JSON, nullable=True)  # Communication, leadership, etc.
    langues = Column(JSON, nullable=True)  # Langues parlées et niveau
    experiences = Column(JSON, nullable=True)  # Stages, bénévolat, jobs
    
    # Dimension 4: Objectifs de carrière
    metiers_vises = Column(JSON, nullable=True)  # Liste des métiers souhaités
    secteur_activite = Column(String(255), nullable=True)  # Santé, Tech, Finance, etc.
    niveau_etudes_vise = Column(String(100), nullable=True)  # Licence, Master, Doctorat
    projet_professionnel = Column(Text, nullable=True)  # Description du projet
    
    # Dimension 5: Contraintes pratiques
    budget_max = Column(Float, nullable=True)  # Budget annuel max
    regions_acceptees = Column(JSON, nullable=True)  # Régions géographiques
    mobilite_internationale = Column(Boolean, default=False)  # Accepte l'étranger
    besoin_bourse = Column(Boolean, default=False)  # Nécessite une bourse
    contraintes_familiales = Column(Text, nullable=True)  # Contraintes particulières
    
    # Dimension 6: Préférences d'apprentissage
    type_etablissement_prefere = Column(String(100), nullable=True)  # Public/Privé
    taille_classe_preferee = Column(String(50), nullable=True)  # Petit/Moyen/Grand
    modalite_enseignement = Column(JSON, nullable=True)  # Présentiel, Hybride, Distance
    environnement_prefere = Column(String(255), nullable=True)  # Urbain, Rural
    
    # Score de complétude du profil
    completeness_score = Column(Float, default=0.0)  # 0-100%
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="student_profile")
    
    def __repr__(self):
        return f"<StudentProfile(id={self.id}, user_id={self.user_id}, completeness={self.completeness_score}%)>"
    
    def calculate_completeness(self):
        """Calcule le score de complétude du profil (0-100%)"""
        total_fields = 20  # Nombre total de champs importants
        filled_fields = 0
        
        # Vérifier chaque dimension
        if self.niveau_actuel:
            filled_fields += 1
        if self.serie_bac:
            filled_fields += 1
        if self.moyenne_generale:
            filled_fields += 1
        if self.matieres_fortes:
            filled_fields += 1
        if self.domaines_interet:
            filled_fields += 1
        if self.activites_extrascolaires:
            filled_fields += 1
        if self.competences_techniques:
            filled_fields += 1
        if self.competences_soft:
            filled_fields += 1
        if self.langues:
            filled_fields += 1
        if self.metiers_vises:
            filled_fields += 1
        if self.secteur_activite:
            filled_fields += 1
        if self.niveau_etudes_vise:
            filled_fields += 1
        if self.budget_max:
            filled_fields += 1
        if self.regions_acceptees:
            filled_fields += 1
        if self.type_etablissement_prefere:
            filled_fields += 1
        if self.modalite_enseignement:
            filled_fields += 1
        if self.projet_professionnel:
            filled_fields += 2  # Plus de poids
        if self.experiences:
            filled_fields += 1
        if self.passions:
            filled_fields += 1
        if self.contraintes_familiales:
            filled_fields += 1
        
        self.completeness_score = (filled_fields / total_fields) * 100
        return self.completeness_score
