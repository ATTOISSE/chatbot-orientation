import pytest
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestCommit2Configuration:
    """Test COMMIT 2: Configuration and Dependencies"""

    def test_config_file_exists(self):
        """Verify config.py exists"""
        config_file = Path(__file__).parent.parent / "backend" / "app" / "config.py"
        assert config_file.exists(), "config.py should exist"

    def test_backend_requirements_exists(self):
        """Verify backend requirements.txt exists"""
        req_file = Path(__file__).parent.parent / "backend" / "requirements.txt"
        assert req_file.exists(), "backend/requirements.txt should exist"

    def test_frontend_requirements_exists(self):
        """Verify frontend requirements.txt exists"""
        req_file = Path(__file__).parent.parent / "frontend" / "requirements.txt"
        assert req_file.exists(), "frontend/requirements.txt should exist"

    def test_backend_dockerfile_exists(self):
        """Verify backend Dockerfile exists"""
        dockerfile = Path(__file__).parent.parent / "backend" / "Dockerfile"
        assert dockerfile.exists(), "backend/Dockerfile should exist"

    def test_frontend_dockerfile_exists(self):
        """Verify frontend Dockerfile exists"""
        dockerfile = Path(__file__).parent.parent / "frontend" / "Dockerfile"
        assert dockerfile.exists(), "frontend/Dockerfile should exist"

    def test_docker_compose_exists(self):
        """Verify docker-compose.yml exists"""
        docker_compose = Path(__file__).parent.parent / "docker-compose.yml"
        assert docker_compose.exists(), "docker-compose.yml should exist"

    def test_backend_requirements_contains_fastapi(self):
        """Verify FastAPI in backend requirements"""
        req_file = Path(__file__).parent.parent / "backend" / "requirements.txt"
        content = req_file.read_text()
        assert "fastapi" in content.lower(), "FastAPI should be in backend requirements"

    def test_backend_requirements_contains_sqlalchemy(self):
        """Verify SQLAlchemy in backend requirements"""
        req_file = Path(__file__).parent.parent / "backend" / "requirements.txt"
        content = req_file.read_text()
        assert "sqlalchemy" in content.lower(), "SQLAlchemy should be in backend requirements"

    def test_backend_requirements_contains_langchain(self):
        """Verify LangChain in backend requirements"""
        req_file = Path(__file__).parent.parent / "backend" / "requirements.txt"
        content = req_file.read_text()
        assert "langchain" in content.lower(), "LangChain should be in backend requirements"

    def test_backend_requirements_contains_chromadb(self):
        """Verify ChromaDB in backend requirements"""
        req_file = Path(__file__).parent.parent / "backend" / "requirements.txt"
        content = req_file.read_text()
        assert "chromadb" in content.lower(), "ChromaDB should be in backend requirements"

    def test_frontend_requirements_contains_streamlit(self):
        """Verify Streamlit in frontend requirements"""
        req_file = Path(__file__).parent.parent / "frontend" / "requirements.txt"
        content = req_file.read_text()
        assert "streamlit" in content.lower(), "Streamlit should be in frontend requirements"

    def test_docker_compose_has_postgres(self):
        """Verify PostgreSQL service in docker-compose.yml"""
        docker_compose = Path(__file__).parent.parent / "docker-compose.yml"
        content = docker_compose.read_text()
        assert "postgres" in content.lower(), "PostgreSQL service should be in docker-compose.yml"

    def test_docker_compose_has_chromadb(self):
        """Verify ChromaDB service in docker-compose.yml"""
        docker_compose = Path(__file__).parent.parent / "docker-compose.yml"
        content = docker_compose.read_text()
        assert "chromadb" in content.lower(), "ChromaDB service should be in docker-compose.yml"

    def test_docker_compose_has_backend(self):
        """Verify backend service in docker-compose.yml"""
        docker_compose = Path(__file__).parent.parent / "docker-compose.yml"
        content = docker_compose.read_text()
        assert "backend" in content.lower(), "Backend service should be in docker-compose.yml"

    def test_docker_compose_has_frontend(self):
        """Verify frontend service in docker-compose.yml"""
        docker_compose = Path(__file__).parent.parent / "docker-compose.yml"
        content = docker_compose.read_text()
        assert "frontend" in content.lower(), "Frontend service should be in docker-compose.yml"

    def test_backend_dockerfile_uses_python311(self):
        """Verify backend Dockerfile uses Python 3.11"""
        dockerfile = Path(__file__).parent.parent / "backend" / "Dockerfile"
        content = dockerfile.read_text()
        assert "python:3.11" in content.lower(), "Backend Dockerfile should use Python 3.11"

    def test_frontend_dockerfile_uses_python311(self):
        """Verify frontend Dockerfile uses Python 3.11"""
        dockerfile = Path(__file__).parent.parent / "frontend" / "Dockerfile"
        content = dockerfile.read_text()
        assert "python:3.11" in content.lower(), "Frontend Dockerfile should use Python 3.11"

    def test_backend_dockerfile_exposes_port_8000(self):
        """Verify backend Dockerfile exposes port 8000"""
        dockerfile = Path(__file__).parent.parent / "backend" / "Dockerfile"
        content = dockerfile.read_text()
        assert "8000" in content, "Backend Dockerfile should expose port 8000"

    def test_frontend_dockerfile_exposes_port_8501(self):
        """Verify frontend Dockerfile exposes port 8501"""
        dockerfile = Path(__file__).parent.parent / "frontend" / "Dockerfile"
        content = dockerfile.read_text()
        assert "8501" in content, "Frontend Dockerfile should expose port 8501"

    def test_config_file_has_settings_class(self):
        """Verify config.py has Settings class"""
        config_file = Path(__file__).parent.parent / "backend" / "app" / "config.py"
        content = config_file.read_text()
        assert "class Settings" in content, "config.py should have Settings class"
        assert "BaseSettings" in content, "Settings should inherit from BaseSettings"

    def test_config_file_has_database_url(self):
        """Verify config.py has DATABASE_URL"""
        config_file = Path(__file__).parent.parent / "backend" / "app" / "config.py"
        content = config_file.read_text()
        assert "DATABASE_URL" in content, "config.py should have DATABASE_URL"

    def test_config_file_has_jwt_secret(self):
        """Verify config.py has JWT_SECRET"""
        config_file = Path(__file__).parent.parent / "backend" / "app" / "config.py"
        content = config_file.read_text()
        assert "JWT_SECRET" in content, "config.py should have JWT_SECRET"

    def test_docker_compose_has_volumes(self):
        """Verify docker-compose.yml has volume definitions"""
        docker_compose = Path(__file__).parent.parent / "docker-compose.yml"
        content = docker_compose.read_text()
        assert "volumes:" in content.lower(), "docker-compose.yml should have volumes section"
        assert "postgres_data" in content.lower(), "docker-compose.yml should have postgres_data volume"
        assert "chromadb_data" in content.lower(), "docker-compose.yml should have chromadb_data volume"

    def test_docker_compose_has_networks(self):
        """Verify docker-compose.yml has network definitions"""
        docker_compose = Path(__file__).parent.parent / "docker-compose.yml"
        content = docker_compose.read_text()
        assert "networks:" in content.lower(), "docker-compose.yml should have networks section"
        assert "eduguide-network" in content.lower(), "docker-compose.yml should have eduguide-network"

    def test_commit_2_documentation_exists(self):
        """Verify COMMIT_2.md exists"""
        doc_file = Path(__file__).parent.parent / "COMMIT_2.md"
        assert doc_file.exists(), "COMMIT_2.md documentation should exist"
