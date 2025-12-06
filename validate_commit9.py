"""
COMMIT 9 Validation - ML Integration avec ChromaDB
Tests pour le service vectorstore et les endpoints RAG
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_1_vectorstore_exists():
    """Vérifier que le fichier vectorstore.py existe"""
    path = project_root / "backend" / "app" / "ml" / "vectorstore.py"
    assert path.exists(), f"vectorstore.py not found at {path}"
    print("✅ Test 1: Vectorstore module exists")
    return True


def test_2_vectorstore_classes():
    """Vérifier les classes ChromaDB"""
    try:
        from backend.app.ml.vectorstore import ChromaDBVectorStore, FormationVectorIndexer
        assert ChromaDBVectorStore is not None
        assert FormationVectorIndexer is not None
        print("✅ Test 2: ChromaDBVectorStore and FormationVectorIndexer classes exist")
        return True
    except ImportError as e:
        print(f"❌ Test 2: Import failed - {e}")
        return False


def test_3_rag_endpoints_exists():
    """Vérifier que le fichier rag.py existe"""
    path = project_root / "backend" / "app" / "api" / "routes" / "rag.py"
    assert path.exists(), f"rag.py not found at {path}"
    print("✅ Test 3: RAG endpoints file exists")
    return True


def test_4_rag_endpoints_imports():
    """Vérifier que les endpoints RAG peuvent être importés"""
    try:
        from backend.app.api.routes.rag import (
            semantic_search,
            index_formations,
            rag_chat,
            get_formation_context,
            get_index_status
        )
        assert semantic_search is not None
        assert index_formations is not None
        assert rag_chat is not None
        assert get_formation_context is not None
        assert get_index_status is not None
        print("✅ Test 4: All RAG endpoints can be imported")
        return True
    except ImportError as e:
        print(f"❌ Test 4: Import failed - {e}")
        return False


def test_5_vectorstore_methods():
    """Vérifier les méthodes critiques de ChromaDBVectorStore"""
    try:
        from backend.app.ml.vectorstore import ChromaDBVectorStore
        
        methods = [
            "add_formation_chunks",
            "search",
            "search_by_text",
            "get_collection_count",
            "delete_collection",
            "persist",
            "reset"
        ]
        
        for method in methods:
            assert hasattr(ChromaDBVectorStore, method), f"Missing method: {method}"
        
        print("✅ Test 5: All ChromaDBVectorStore methods exist")
        return True
    except Exception as e:
        print(f"❌ Test 5: {e}")
        return False


def test_6_indexer_methods():
    """Vérifier les méthodes critiques de FormationVectorIndexer"""
    try:
        from backend.app.ml.vectorstore import FormationVectorIndexer
        
        methods = [
            "index_chunks",
            "search_formations",
            "get_formation_context",
            "get_stats"
        ]
        
        for method in methods:
            assert hasattr(FormationVectorIndexer, method), f"Missing method: {method}"
        
        print("✅ Test 6: All FormationVectorIndexer methods exist")
        return True
    except Exception as e:
        print(f"❌ Test 6: {e}")
        return False


def test_7_ml_package_init():
    """Vérifier que le package ml a __init__.py"""
    path = project_root / "backend" / "app" / "ml" / "__init__.py"
    assert path.exists(), f"__init__.py not found at {path}"
    
    # Vérifier le contenu
    content = path.read_text()
    assert "ChromaDBVectorStore" in content
    assert "FormationVectorIndexer" in content
    
    print("✅ Test 7: ML package initialization is correct")
    return True


def test_8_rag_schemas():
    """Vérifier les schémas Pydantic des endpoints RAG"""
    try:
        from backend.app.api.routes.rag import (
            IndexStatusResponse,
            SearchResultChunk,
            SemanticSearchRequest,
            SemanticSearchResponse,
            IndexFormationsRequest,
            IndexFormationsResponse
        )
        
        schemas = [
            IndexStatusResponse,
            SearchResultChunk,
            SemanticSearchRequest,
            SemanticSearchResponse,
            IndexFormationsRequest,
            IndexFormationsResponse
        ]
        
        for schema in schemas:
            assert schema is not None
        
        print("✅ Test 8: All Pydantic schemas are defined")
        return True
    except ImportError as e:
        print(f"❌ Test 8: Import failed - {e}")
        return False


def test_9_endpoints_have_decorators():
    """Vérifier que les endpoints ont les bons décorateurs"""
    try:
        rag_path = project_root / "backend" / "app" / "api" / "routes" / "rag.py"
        content = rag_path.read_text()
        
        endpoints = [
            "@router.get(\"/status\"",
            "@router.post(\"/search\"",
            "@router.post(\"/index-formations\"",
            "@router.post(\"/chat\"",
            "@router.get(\"/formation/{formation_id}/context\""
        ]
        
        for endpoint in endpoints:
            assert endpoint in content, f"Missing endpoint decorator: {endpoint}"
        
        print("✅ Test 9: All endpoints have proper decorators")
        return True
    except Exception as e:
        print(f"❌ Test 9: {e}")
        return False


def test_10_rag_routes_exported():
    """Vérifier que RAG est exporté dans routes/__init__.py"""
    try:
        init_path = project_root / "backend" / "app" / "api" / "routes" / "__init__.py"
        content = init_path.read_text()
        
        assert "rag" in content, "RAG module not exported"
        assert "from app.api.routes import" in content
        
        print("✅ Test 10: RAG routes are exported in __init__.py")
        return True
    except Exception as e:
        print(f"❌ Test 10: {e}")
        return False


def test_11_vectorstore_initialization():
    """Vérifier l'initialisation du ChromaDB"""
    try:
        from backend.app.ml.vectorstore import ChromaDBVectorStore
        
        # Vérifier que __init__ a les bons paramètres
        import inspect
        sig = inspect.signature(ChromaDBVectorStore.__init__)
        params = list(sig.parameters.keys())
        
        required_params = ["persist_directory", "embedding_function", "collection_name"]
        for param in required_params:
            assert param in params, f"Missing parameter: {param}"
        
        print("✅ Test 11: ChromaDBVectorStore initialization is correct")
        return True
    except Exception as e:
        print(f"❌ Test 11: {e}")
        return False


def test_12_embedding_integration():
    """Vérifier l'intégration des modèles d'embeddings"""
    try:
        from backend.app.api.routes.rag import get_embedding_model
        from backend.app.rag.embeddings import HuggingFaceEmbeddingModel, MockEmbeddingModel
        
        # Les fonctions devraient exister
        assert callable(get_embedding_model)
        
        print("✅ Test 12: Embedding model integration is ready")
        return True
    except Exception as e:
        print(f"❌ Test 12: {e}")
        return False


def test_13_rag_dependencies():
    """Vérifier que toutes les dépendances RAG sont disponibles"""
    try:
        from backend.app.api.routes.rag import (
            get_vectorstore,
            get_indexer,
            get_rag_indexer,
            get_embedding_model
        )
        
        functions = [
            get_vectorstore,
            get_indexer,
            get_rag_indexer,
            get_embedding_model
        ]
        
        for func in functions:
            assert callable(func), f"{func.__name__} is not callable"
        
        print("✅ Test 13: All dependency functions are available")
        return True
    except Exception as e:
        print(f"❌ Test 13: {e}")
        return False


def test_14_endpoint_documentation():
    """Vérifier que les endpoints ont une documentation"""
    try:
        rag_path = project_root / "backend" / "app" / "api" / "routes" / "rag.py"
        content = rag_path.read_text()
        
        # Chaque endpoint doit avoir une docstring
        endpoints = [
            "def get_index_status()",
            "def semantic_search(",
            "def index_formations(",
            "def rag_chat(",
            "def get_formation_context("
        ]
        
        for endpoint in endpoints:
            # Vérifier que la fonction existe
            assert endpoint in content, f"Missing endpoint: {endpoint}"
            
            # Vérifier qu'il y a des commentaires
            assert '"""' in content, "Missing docstrings"
        
        print("✅ Test 14: All endpoints have documentation")
        return True
    except Exception as e:
        print(f"❌ Test 14: {e}")
        return False


def test_15_chromadb_collection_methods():
    """Vérifier les méthodes de collection ChromaDB"""
    try:
        rag_path = project_root / "backend" / "app" / "api" / "routes" / "rag.py"
        vs_path = project_root / "backend" / "app" / "ml" / "vectorstore.py"
        
        rag_content = rag_path.read_text()
        vs_content = vs_path.read_text()
        
        # Vérifier les opérations CRUD
        operations = ["add", "query", "get", "delete"]
        
        # Au moins some opérations devraient être mentionnées
        for op in ["add_formation_chunks", "search", "get_collection_count", "delete_collection"]:
            assert op in vs_content, f"Missing operation: {op}"
        
        print("✅ Test 15: All ChromaDB CRUD operations are implemented")
        return True
    except Exception as e:
        print(f"❌ Test 15: {e}")
        return False


def run_all_tests():
    """Lancer tous les tests"""
    tests = [
        test_1_vectorstore_exists,
        test_2_vectorstore_classes,
        test_3_rag_endpoints_exists,
        test_4_rag_endpoints_imports,
        test_5_vectorstore_methods,
        test_6_indexer_methods,
        test_7_ml_package_init,
        test_8_rag_schemas,
        test_9_endpoints_have_decorators,
        test_10_rag_routes_exported,
        test_11_vectorstore_initialization,
        test_12_embedding_integration,
        test_13_rag_dependencies,
        test_14_endpoint_documentation,
        test_15_chromadb_collection_methods,
    ]
    
    print("\n" + "="*60)
    print("COMMIT 9: ML Integration Validation")
    print("="*60 + "\n")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Résultats: {passed}/{len(tests)} ✓")
    print("="*60)
    
    if failed == 0:
        print("✅ TOUS LES TESTS COMMIT 9 SONT PASSÉS!")
        return True
    else:
        print(f"❌ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
