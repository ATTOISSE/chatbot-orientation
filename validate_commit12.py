#!/usr/bin/env python3
"""
COMMIT 12: Validation des endpoints LLM Integration
Tests simples sans dépendances FastAPI
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Import seulement les modules core (pas les routes)
from app.ml.llm_service import (
    OllamaLLM, MockLLM, LLMService, PromptBuilder, LLMConfig
)

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_test(num, name, result):
    status = "OK" if result else "FAIL"
    print(f"[{status}] Test {num}: {name}")
    return result

# Tests

def test_1():
    try:
        llm = OllamaLLM(model_name="llama2", api_url="http://localhost:11434", temperature=0.7, max_tokens=512)
        return llm is not None and llm.model_name == "llama2"
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_2():
    try:
        llm = MockLLM()
        return llm is not None
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_3():
    try:
        config = LLMConfig(model_name="llama2", api_url="http://localhost:11434", temperature=0.7, max_tokens=512)
        service = LLMService(config)
        return service is not None
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_4():
    try:
        llm = MockLLM()
        response = llm.generate_response("Bonjour")
        return response and len(response) > 0 and isinstance(response, str)
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_5():
    try:
        prompt = PromptBuilder.build_chat_prompt("Qu'est-ce qu'une formation?")
        return prompt and len(prompt) > 0 and "formation" in prompt.lower()
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_6():
    try:
        formations = [{"id": 1, "intitule": "Ingénieur Informatique", "domaine": "Informatique", "duree": "3 ans"}]
        prompt = PromptBuilder.build_context_prompt(formations, "Informatique?")
        return prompt and "Informatique" in prompt and "Ing" in prompt
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_7():
    try:
        config = LLMConfig(model_name="mistral")
        service = LLMService(config)
        return service.get_model_name() == "mistral"
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_8():
    try:
        config = LLMConfig()
        return config.model_name is not None and config.api_url is not None and config.temperature > 0 and config.max_tokens > 0
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_9():
    try:
        config = LLMConfig(model_name="llama2", api_url="http://localhost:99999")
        service = LLMService(config)
        response = service.generate_response("Test")
        return response and len(response) > 0
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_10():
    try:
        llm = MockLLM()
        async def test():
            chunks = []
            async for chunk in llm.stream_response("Bonjour"):
                chunks.append(chunk)
            return len(chunks) > 0 and all(isinstance(c, str) for c in chunks)
        return asyncio.run(test())
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_11():
    try:
        config = LLMConfig()
        service = LLMService(config)
        info = service.get_info()
        return info and isinstance(info, dict) and "type" in info
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_12():
    try:
        config = LLMConfig(model_name="neural-chat", temperature=0.5, max_tokens=256)
        return config.model_name == "neural-chat" and config.temperature == 0.5 and config.max_tokens == 256
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_13():
    try:
        prompt = PromptBuilder.build_system_prompt()
        return prompt and len(prompt) > 0 and ("educatif" in prompt.lower() or "assistant" in prompt.lower())
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_14():
    try:
        config = LLMConfig()
        service = LLMService(config)
        async def test():
            chunks = []
            async for chunk in service.stream_response("Test"):
                chunks.append(chunk)
            return len(chunks) > 0
        return asyncio.run(test())
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_15():
    try:
        llm = MockLLM()
        response1 = llm.generate_response("Informatique")
        response2 = llm.generate_response("Informatique")
        return len(response1) > 0 and len(response2) > 0 and isinstance(response1, str)
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_16():
    try:
        config = LLMConfig()
        service = LLMService(config)
        result = service.is_available()
        return isinstance(result, bool)
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_17():
    try:
        formations = [
            {"nom": "Ingénieur Informatique", "domaine": "Informatique"},
            {"nom": "Analyste de Données", "domaine": "Informatique"},
            {"nom": "Développeur Web", "domaine": "Informatique"},
        ]
        prompt = PromptBuilder.build_context_prompt(formations, "Programmation")
        return len(prompt) > 0 and prompt.count("Informatique") >= 3
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_18():
    try:
        llm = OllamaLLM(model_name="mistral", temperature=1.5)
        return llm.temperature == 1.5
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_19():
    try:
        llm = MockLLM()
        response = llm.generate_response("test")
        return isinstance(response, str) and len(response.strip()) > 0
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_20():
    try:
        models = ["llama2", "mistral", "neural-chat", "dolphin"]
        results = []
        for model in models:
            config = LLMConfig(model_name=model)
            service = LLMService(config)
            results.append(service.get_model_name() == model)
        return all(results)
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print_header("COMMIT 12: LLM Integration Tests")
    
    tests = [
        ("OllamaLLM instantiation", test_1),
        ("MockLLM instantiation", test_2),
        ("LLMService creation", test_3),
        ("MockLLM generates text", test_4),
        ("PromptBuilder chat prompt", test_5),
        ("PromptBuilder context prompt", test_6),
        ("LLMService model name", test_7),
        ("LLMConfig defaults", test_8),
        ("LLMService fallback", test_9),
        ("MockLLM streaming", test_10),
        ("LLMService get_info", test_11),
        ("LLMConfig custom", test_12),
        ("PromptBuilder system prompt", test_13),
        ("LLMService async generate", test_14),
        ("MockLLM consistency", test_15),
        ("LLMService is_available", test_16),
        ("PromptBuilder long context", test_17),
        ("OllamaLLM temperature", test_18),
        ("MockLLM has responses", test_19),
        ("LLMService multiple models", test_20),
    ]
    
    passed = 0
    failed = 0
    
    for i, (name, test_func) in enumerate(tests, 1):
        if print_test(i, name, test_func()):
            passed += 1
        else:
            failed += 1
    
    print_header(f"Résultats: {passed}/{len(tests)}")
    
    if failed == 0:
        print(f"[SUCCESS] TOUS LES TESTS COMMIT 12 SONT PASSES!")
        return 0
    else:
        print(f"[FAILED] {failed} test(s) echoue(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
