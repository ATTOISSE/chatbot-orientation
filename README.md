# EduGuide Sénégal - Chatbot d'Orientation Académique

## 🎯 Plateforme d'Orientation pour Études Supérieures au Sénégal

Une plateforme web complète basée sur **Llama 3 LLM** pour aider les étudiants sénégalais à trouver leur formation idéale.

### ✨ Fonctionnalités Principales

- 🤖 **Chatbot Conversationnel RAG** - Interaction naturelle en français
- 🔍 **Moteur de Recherche Multi-Critères** - Filtres avancés sur formations
- 📊 **Système de Recommandation IA** - Suggestions personnalisées basées sur profil
- 👤 **Profil Étudiant 6D** - Auto-évaluation guidée (académique, intérêts, budget, géographie, aspirations, disponibilité)
- ⚖️ **Outil de Comparaison** - Comparer jusqu'à 3 formations simultanément
- 📈 **Traçabilité Données** - Source, fraîcheur et fiabilité de chaque info
- 🔐 **Authentification JWT** - Sécurisation des données utilisateur

### 🛠 Stack Technologique

**Backend:**
- FastAPI (async, high-performance)
- PostgreSQL (données relationnelles)
- ChromaDB (vecteurs RAG)
- Llama 3 (LLM via Hugging Face)
- LangChain (orchestration RAG)
- SQLAlchemy (ORM)

**Frontend:**
- Streamlit (interface interactive)
- Requests/httpx (client API)

**Infrastructure:**
- Docker + Docker Compose
- Python 3.11

### 📋 Prérequis

- Python 3.11+
- Docker & Docker Compose
- Hugging Face API Key (pour Llama 3)
- PostgreSQL 15+

### 🚀 Installation & Démarrage

```bash
# 1. Cloner le projet
cd chatbot-orientation

# 2. Copier le fichier .env
cp .env.example .env

# 3. Configurer les variables (éditer .env)
# - HUGGINGFACE_API_KEY
# - JWT_SECRET
# - DATABASE_URL (optionnel si Docker)

# 4. Lancer les services
docker-compose up --build

# 5. Accès
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 📚 Architecture

```
chatbot-orientation/
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── config.py            # Configuration Pydantic
│   │   ├── auth/                # JWT & authentification
│   │   ├── api/routes/          # Endpoints API
│   │   ├── models/              # Modèles SQLAlchemy
│   │   ├── services/            # Logique métier
│   │   ├── database/            # DB connection
│   │   ├── rag/                 # Llama 3 + RAG
│   │   └── utils/               # Utilitaires
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py                   # Point d'entrée Streamlit
│   ├── pages/                   # Pages multi-page
│   ├── components/              # Composants réutilisables
│   ├── requirements.txt
│   └── Dockerfile
├── datas/                       # Données JSON (formations, écoles, accréditations)
├── scripts/                     # Scripts d'initialisation
├── tests/                       # Tests unitaires
├── docker-compose.yml
├── .env.example
└── README.md
```

### 🗄️ Structure Données

**Données initiales:**
- ~100 établissements sénégalais
- ~1000+ formations détaillées
- ~600+ programmes accrédités CAMES
- Automatiquement enrichies (durée, niveau, taux insertion, etc.)

**Tables principales:**
- `users` - Utilisateurs authentifiés
- `formations` - Formations avec descriptions
- `etablissements` - Universités & écoles
- `domaines` - Domaines d'études
- `conversations` - Historique chat
- `messages` - Messages utilisateurs & chatbot
- `recommendations` - Recommandations IA
- `data_sources` - Traçabilité données

### 🔑 Endpoints API Principaux

**Auth:**
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion (JWT)
- `GET /auth/me` - Profil utilisateur

**Formations:**
- `GET /formations/search` - Recherche multi-critères
- `GET /formations/{id}` - Détails formation

**Chat RAG:**
- `POST /chat/message` - Envoyer question au chatbot
- `GET /chat/history` - Historique conversations
- `DELETE /chat/{id}` - Supprimer conversation

**Recommandations:**
- `GET /recommendations/{user_id}` - Obtenir recommandations personnalisées

**Profil:**
- `POST /profile` - Créer profil étudiant
- `GET /profile/{user_id}` - Récupérer profil
- `PUT /profile/{user_id}` - Mettre à jour profil

**Comparaison:**
- `POST /comparison/compare` - Comparer formations

**Documentation interactive:** http://localhost:8000/docs

### 📖 Cas d'Usage

**Étudiant bachelier:**
1. S'inscrire sur la plateforme
2. Remplir son profil (6 dimensions)
3. Discuter avec le chatbot sur ses options
4. Voir recommandations personnalisées
5. Comparer 2-3 formations intéressantes
6. Consulter sources & accréditations

### 🧪 Tests

```bash
# Lancer les tests unitaires
pytest tests/

# Avec couverture
pytest --cov=app tests/
```

### 🤝 Contribution

1. Créer une branche feature: `git checkout -b feature/amazing-feature`
2. Commit: `git commit -m 'Add amazing feature'`
3. Push: `git push origin feature/amazing-feature`
4. Ouvrir une Pull Request

### 📝 Licence

MIT License - Voir `LICENSE` pour plus de détails

### 👥 Auteur

Développé pour l'orientation académique au Sénégal

### 📞 Support

Pour les issues ou questions:
- Ouvrir une issue GitHub
- Email: support@eduguide-senegal.sn

---

**Version:** 1.0.0  
**Dernière mise à jour:** Décembre 2025
