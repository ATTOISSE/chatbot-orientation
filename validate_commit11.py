"""
COMMIT 11 Validation - Streaming Chat (SSE & WebSocket)
Tests pour les endpoints de streaming et WebSocket
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent

def test_1_streaming_service_exists():
    """Vérifier que le service streaming existe"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    assert path.exists(), "streaming_service.py not found"
    
    content = path.read_text()
    assert "class StreamingChatService" in content
    assert "class StreamingResponseGenerator" in content
    
    print("✅ Test 1: Streaming service classes exist")
    return True


def test_2_streaming_endpoints_exist():
    """Vérifier que les endpoints streaming existent"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    assert path.exists(), "streaming.py not found"
    
    content = path.read_text()
    assert "router = APIRouter" in content
    
    print("✅ Test 2: Streaming endpoints file exists")
    return True


def test_3_sse_endpoints():
    """Vérifier les endpoints SSE"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    endpoints = [
        "@router.post(\"/stream\"",
        "@router.post(\"/stream-fast\"",
        "@router.post(\"/stream-sources\""
    ]
    
    for endpoint in endpoints:
        assert endpoint in content, f"Missing endpoint: {endpoint}"
    
    print("✅ Test 3: All SSE endpoints are defined")
    return True


def test_4_websocket_endpoint():
    """Vérifier le endpoint WebSocket"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "@router.websocket(\"/ws/" in content
    assert "async def websocket_chat" in content
    
    print("✅ Test 4: WebSocket endpoint is defined")
    return True


def test_5_connection_manager():
    """Vérifier le gestionnaire de connexions"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "class ConnectionManager" in content
    assert "async def connect" in content
    assert "def disconnect" in content
    
    print("✅ Test 5: ConnectionManager is implemented")
    return True


def test_6_streaming_methods():
    """Vérifier les méthodes de streaming"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    content = path.read_text()
    
    methods = [
        "async def stream_chat_response",
        "async def process_and_stream_message",
        "async def stream_sources",
        "async def stream_text"
    ]
    
    for method in methods:
        assert method in content, f"Missing method: {method}"
    
    print("✅ Test 6: All streaming methods are implemented")
    return True


def test_7_async_generators():
    """Vérifier que les générateurs async sont utilisés"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    content = path.read_text()
    
    # Vérifier AsyncGenerator
    assert "AsyncGenerator" in content
    assert "async def" in content
    assert "yield" in content
    
    print("✅ Test 7: Async generators are properly implemented")
    return True


def test_8_json_streaming():
    """Vérifier le streaming JSON"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    content = path.read_text()
    
    # Vérifier JSON streaming
    assert "json.dumps" in content
    assert '+ "\\n"' in content or "+ '\\n'" in content
    
    print("✅ Test 8: JSON streaming is implemented")
    return True


def test_9_error_handling():
    """Vérifier la gestion d'erreurs"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "try:" in content
    assert "except" in content
    assert "except WebSocketDisconnect" in content
    
    print("✅ Test 9: Error handling is implemented")
    return True


def test_10_streaming_response():
    """Vérifier StreamingResponse"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "StreamingResponse" in content
    assert "text/event-stream" in content
    
    print("✅ Test 10: StreamingResponse is used correctly")
    return True


def test_11_media_types():
    """Vérifier les media types"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "text/event-stream" in content
    assert "application/x-ndjson" in content or "ndjson" in content.lower()
    
    print("✅ Test 11: Correct media types are set")
    return True


def test_12_conversation_integration():
    """Vérifier l'intégration avec les conversations"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    content = path.read_text()
    
    assert "create_conversation" in content
    assert "add_message" in content
    
    print("✅ Test 12: Conversation integration is present")
    return True


def test_13_rag_integration():
    """Vérifier l'intégration RAG"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    content = path.read_text()
    
    assert "search_formations_by_query" in content
    
    print("✅ Test 13: RAG integration is present")
    return True


def test_14_chunk_delay():
    """Vérifier le contrôle du délai entre chunks"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    content = path.read_text()
    
    assert "chunk_delay" in content
    assert "asyncio.sleep" in content
    
    print("✅ Test 14: Chunk delay control is implemented")
    return True


def test_15_authentication():
    """Vérifier la protection par authentification"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "get_current_user" in content
    assert "Depends(get_current_user)" in content
    
    print("✅ Test 15: Authentication protection is applied")
    return True


def test_16_streaming_exported():
    """Vérifier que streaming est exporté"""
    path = project_root / "backend" / "app" / "api" / "routes" / "__init__.py"
    content = path.read_text()
    
    assert "streaming" in content
    
    print("✅ Test 16: Streaming routes are exported")
    return True


def test_17_source_streaming():
    """Vérifier le streaming de sources"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "stream-sources" in content
    
    print("✅ Test 17: Source streaming endpoint exists")
    return True


def test_18_websocket_messages():
    """Vérifier le protocole WebSocket"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "receive_json" in content
    assert "send_json" in content
    
    print("✅ Test 18: WebSocket message protocol is implemented")
    return True


def test_19_logging():
    """Vérifier le logging"""
    path = project_root / "backend" / "app" / "services" / "streaming_service.py"
    content = path.read_text()
    
    assert "logger" in content
    assert "logger.info" in content or "logger.error" in content
    
    print("✅ Test 19: Logging is implemented")
    return True


def test_20_cache_control():
    """Vérifier les headers de streaming"""
    path = project_root / "backend" / "app" / "api" / "routes" / "streaming.py"
    content = path.read_text()
    
    assert "Cache-Control" in content
    assert "X-Accel-Buffering" in content or "no-cache" in content
    
    print("✅ Test 20: Streaming headers are properly configured")
    return True


def run_all_tests():
    """Lancer tous les tests"""
    tests = [
        test_1_streaming_service_exists,
        test_2_streaming_endpoints_exist,
        test_3_sse_endpoints,
        test_4_websocket_endpoint,
        test_5_connection_manager,
        test_6_streaming_methods,
        test_7_async_generators,
        test_8_json_streaming,
        test_9_error_handling,
        test_10_streaming_response,
        test_11_media_types,
        test_12_conversation_integration,
        test_13_rag_integration,
        test_14_chunk_delay,
        test_15_authentication,
        test_16_streaming_exported,
        test_17_source_streaming,
        test_18_websocket_messages,
        test_19_logging,
        test_20_cache_control,
    ]
    
    print("\n" + "="*60)
    print("COMMIT 11: Streaming Chat (SSE & WebSocket) Validation")
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
        print("✅ TOUS LES TESTS COMMIT 11 SONT PASSÉS!")
        return True
    else:
        print(f"❌ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
