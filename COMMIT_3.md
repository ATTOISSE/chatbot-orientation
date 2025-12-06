# COMMIT 3: Database Models (SQLAlchemy)

## 📋 Summary

Complete database schema with SQLAlchemy ORM models for all entities: users, conversations, formations, establishments, and student profiles.

## 📁 Files Created

### Database Configuration
- ✅ `backend/app/database/base.py` - SQLAlchemy engine, session, Base class
- ✅ `backend/app/database/init_db.py` - Database initialization script

### Models
- ✅ `backend/app/models/user.py` - User model (authentication + profile)
- ✅ `backend/app/models/conversation.py` - Conversation & Message models (chat history)
- ✅ `backend/app/models/formation.py` - Formation, Etablissement, Domaine, DataSource models
- ✅ `backend/app/models/student_profile.py` - StudentProfile model (6D profiling)
- ✅ `backend/app/models/__init__.py` - Centralized model imports

### Alembic Migrations
- ✅ `backend/alembic.ini` - Alembic configuration
- ✅ `backend/alembic/env.py` - Migration environment
- ✅ `backend/alembic/script.py.mako` - Migration template

## 🗄️ Database Schema

### 8 Tables Created:

#### 1. **users** (Utilisateurs)
```
- id, email, username, hashed_password
- full_name, niveau_etude, domaine_interet, region_preference
- is_active, is_superuser
- created_at, updated_at
- Relations: conversations (1-N), student_profile (1-1)
```

#### 2. **conversations** (Historique chat)
```
- id, user_id, title, context
- created_at, updated_at
- Relations: user (N-1), messages (1-N)
```

#### 3. **messages** (Messages chat)
```
- id, conversation_id, role (user/assistant/system)
- content, rag_sources, confidence_score
- created_at
- Relations: conversation (N-1)
```

#### 4. **etablissements** (Établissements)
```
- id, nom, type_etablissement (Public/Privé)
- ville, region, adresse, telephone, email, site_web
- created_at, updated_at
- Relations: formations (1-N)
```

#### 5. **domaines** (Domaines d'études)
```
- id, nom, description, parent_id (hiérarchie)
- created_at
- Relations: formations (N-N), parent/sous_domaines (self-referential)
```

#### 6. **formations** (Formations académiques)
```
- id, intitule, diplome, niveau, duree
- etablissement_id, conditions_admission, objectifs, debouches
- cout_inscription, bourses_disponibles
- est_accredite, organisme_accreditation
- data_source_id
- created_at, updated_at
- Relations: etablissement (N-1), domaines (N-N), data_source (N-1)
```

#### 7. **data_sources** (Sources de données)
```
- id, nom, type_source, url, description
- fiabilite (0-1), derniere_maj
- created_at
- Relations: formations (1-N)
```

#### 8. **student_profiles** (Profils étudiants 6D)
```
6 DIMENSIONS:

D1 - Académique:
  - niveau_actuel, serie_bac, moyenne_generale
  - matieres_fortes, matieres_faibles (JSON)

D2 - Centres d'intérêt:
  - domaines_interet, activites_extrascolaires (JSON)
  - passions

D3 - Compétences:
  - competences_techniques, competences_soft (JSON)
  - langues, experiences (JSON)

D4 - Objectifs:
  - metiers_vises (JSON), secteur_activite
  - niveau_etudes_vise, projet_professionnel

D5 - Contraintes:
  - budget_max, regions_acceptees (JSON)
  - mobilite_internationale, besoin_bourse
  - contraintes_familiales

D6 - Préférences:
  - type_etablissement_prefere, taille_classe_preferee
  - modalite_enseignement (JSON), environnement_prefere

- completeness_score (0-100%)
- created_at, updated_at
- Relations: user (1-1)
```

#### 9. **formation_domaine** (Association N-N)
```
- formation_id, domaine_id
```

## 🔗 Relations Clés

```
User (1) ─────────── (N) Conversation
User (1) ─────────── (1) StudentProfile
Conversation (1) ──── (N) Message
Etablissement (1) ─── (N) Formation
Formation (N) ──────── (N) Domaine (via formation_domaine)
DataSource (1) ────── (N) Formation
Domaine (1) ────────── (N) Domaine (hiérarchie parent/enfant)
```

## ✨ Features Principales

### 1. User Model
- Authentification (email, username, password)
- Profil basique (niveau_etude, domaines d'intérêt)
- Gestion des rôles (is_active, is_superuser)
- Soft delete support

### 2. Conversation System
- Historique complet des conversations
- Messages avec rôles (user/assistant/system)
- Métadonnées RAG (sources, confidence score)
- Cascade delete (supprimer user = supprimer conversations)

### 3. Formation Database
- Informations complètes (intitulé, diplôme, durée)
- Coûts et bourses
- Accréditation ANAQ-Sup
- Relations multiples (établissement, domaines)
- Traçabilité (data_source)

### 4. Student Profile 6D
- **Dimension 1**: Parcours académique complet
- **Dimension 2**: Intérêts et passions
- **Dimension 3**: Compétences techniques et soft skills
- **Dimension 4**: Objectifs professionnels
- **Dimension 5**: Contraintes pratiques (budget, géographie)
- **Dimension 6**: Préférences d'apprentissage
- **Score de complétude** auto-calculé (méthode `calculate_completeness()`)

### 5. Data Traceability
- Table `data_sources` pour tracer l'origine
- Score de fiabilité (0-1)
- Date de dernière mise à jour
- Type de source (API, Scraping, Manuel)

## 🧪 Testing Instructions

### Test 1: Vérifier la structure des modèles
```powershell
cd c:\ATTOISSE\eduGuide\chatbot-orientation\backend

# Vérifier que tous les modèles existent
Get-ChildItem -Recurse -Filter "*.py" -Path app\models | Select-Object Name

# Expected output:
# user.py
# conversation.py
# formation.py
# student_profile.py
# __init__.py
```

### Test 2: Vérifier les imports
```powershell
# Tester l'import de tous les modèles (dans Docker)
docker-compose run backend python -c "from app.models import *; print('✅ All models imported')"

# Expected: ✅ All models imported
```

### Test 3: Initialiser la base de données
```powershell
# Créer les tables (dans Docker)
docker-compose run backend python -m app.database.init_db

# Expected output:
# 🔧 Création des tables de la base de données...
# ✅ Tables créées avec succès!
# Tables créées:
#   - users
#   - conversations
#   - messages
#   - etablissements
#   - domaines
#   - formations
#   - data_sources
#   - student_profiles
#   - formation_domaine
```

### Test 4: Vérifier Alembic
```powershell
cd backend

# Générer une migration initiale
docker-compose run backend alembic revision --autogenerate -m "Initial migration"

# Appliquer les migrations
docker-compose run backend alembic upgrade head

# Voir l'historique
docker-compose run backend alembic history
```

### Test 5: Compter les tables
```powershell
# Se connecter à PostgreSQL et compter les tables
docker-compose exec postgres psql -U eduguide -d eduguide_db -c "\dt"

# Expected: 9 tables (8 modèles + 1 alembic_version)
```

### Test 6: Vérifier les colonnes JSON
```powershell
# Vérifier que student_profiles a des colonnes JSON
docker-compose exec postgres psql -U eduguide -d eduguide_db -c "\d student_profiles"

# Expected: Colonnes avec type 'json' pour domaines_interet, competences_techniques, etc.
```

## 📋 Model Summary

| Model | Table | Primary Relations | JSON Fields | Special Features |
|-------|-------|------------------|-------------|------------------|
| User | users | conversations, student_profile | - | Authentication, soft delete |
| Conversation | conversations | user, messages | - | Cascade delete |
| Message | messages | conversation | rag_sources | Enum role, confidence score |
| Etablissement | etablissements | formations | - | Geographic indexing |
| Domaine | domaines | formations, parent | - | Hierarchical (self-ref) |
| Formation | formations | etablissement, domaines, data_source | - | Many-to-many with domaines |
| DataSource | data_sources | formations | - | Reliability scoring |
| StudentProfile | student_profiles | user | 10+ JSON fields | 6D profiling, completeness |

## 📊 JSON Fields in StudentProfile

```python
# Arrays/Lists
- matieres_fortes: ["Mathématiques", "Physique"]
- matieres_faibles: ["Français", "Histoire"]
- domaines_interet: ["Informatique", "IA"]
- activites_extrascolaires: ["Football", "Théâtre"]
- competences_techniques: ["Python", "Excel"]
- competences_soft: ["Leadership", "Communication"]
- langues: [{"langue": "Français", "niveau": "C2"}]
- experiences: [{"type": "Stage", "lieu": "...", "duree": "3 mois"}]
- metiers_vises: ["Data Scientist", "Ingénieur IA"]
- regions_acceptees: ["Dakar", "Thiès", "Saint-Louis"]
- modalite_enseignement: ["Présentiel", "Hybride"]
```

## 📝 Commit Message

```
feat: Add SQLAlchemy database models and schema

- Create database configuration (base.py, init_db.py)
- Add User model with authentication fields
- Add Conversation and Message models for chat history
- Add Formation, Etablissement, Domaine, DataSource models
- Add StudentProfile model with 6D profiling system
- Configure Alembic for database migrations
- Add many-to-many relationship (formation_domaine)
- Add hierarchical domains (self-referential)
- Add JSON fields for flexible data storage
- Add completeness calculation for student profiles
- Add cascade delete for data integrity
- Add indexes for performance optimization
```

## ✅ Status

**READY FOR COMMIT 3** ✅

## 🔜 Next Steps (COMMIT 4)

- Create JWT authentication utilities
- Implement password hashing with bcrypt
- Create token generation and validation
- Add OAuth2 password bearer scheme

---

**Status:** ✅ READY FOR COMMIT 3  
**Next:** COMMIT 4 - Authentication (JWT & Hashing)
