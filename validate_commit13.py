#!/usr/bin/env python3
"""
COMMIT 13: Validation du Frontend Streamlit
Tests pour verifier l'interface utilisateur
"""

import sys
import os

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
    """Frontend folder exists"""
    try:
        return os.path.exists("frontend/streamlit")
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_2():
    """app.py exists"""
    try:
        return os.path.exists("frontend/streamlit/app.py")
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_3():
    """requirements.txt exists"""
    try:
        return os.path.exists("frontend/streamlit/requirements.txt")
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_4():
    """app.py contains streamlit import"""
    try:
        with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            return "import streamlit" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_5():
    """app.py contains page config"""
    try:
        with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            return "st.set_page_config" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_6():
    """requirements.txt contains streamlit"""
    try:
        with open("frontend/streamlit/requirements.txt", "r") as f:
            content = f.read()
            return "streamlit" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_7():
    """requirements.txt contains requests"""
    try:
        with open("frontend/streamlit/requirements.txt", "r") as f:
            content = f.read()
            return "requests" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_8():
    """Config folder exists"""
    try:
        return os.path.exists("frontend/streamlit/.streamlit")
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_9():
    """config.toml exists"""
    try:
        return os.path.exists("frontend/streamlit/.streamlit/config.toml")
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_10():
    """.env.example exists"""
    try:
        return os.path.exists("frontend/streamlit/.env.example")
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_11():
    """run.bat exists"""
    try:
        return os.path.exists("frontend/streamlit/run.bat")
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_12():
    """app.py has main function"""
    try:
        with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            return "def main" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_13():
    """app.py has chat interface"""
    try:
        with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            return "chat" in content.lower()
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_14():
    """app.py has API integration"""
    try:
        with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            return "requests." in content or "API_URL" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_15():
    """app.py has sidebar"""
    try:
        with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            return "st.sidebar" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_16():
    """run.bat has correct command"""
    try:
        with open("frontend/streamlit/run.bat", "r") as f:
            content = f.read()
            return "streamlit run" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_17():
    """config.toml has theme settings"""
    try:
        with open("frontend/streamlit/.streamlit/config.toml", "r") as f:
            content = f.read()
            return "theme" in content.lower()
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_18():
    """.env.example has API_URL"""
    try:
        with open("frontend/streamlit/.env.example", "r") as f:
            content = f.read()
            return "API_URL" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_19():
    """app.py mentions COMMIT 13"""
    try:
        with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            return "COMMIT 13" in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_20():
    """app.py file is not empty"""
    try:
        size = os.path.getsize("frontend/streamlit/app.py")
        return size > 1000  # At least 1KB
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print_header("COMMIT 13: Streamlit Frontend Tests")
    
    tests = [
        ("Frontend folder exists", test_1),
        ("app.py exists", test_2),
        ("requirements.txt exists", test_3),
        ("app.py contains streamlit import", test_4),
        ("app.py contains page config", test_5),
        ("requirements.txt contains streamlit", test_6),
        ("requirements.txt contains requests", test_7),
        ("Config folder exists", test_8),
        ("config.toml exists", test_9),
        (".env.example exists", test_10),
        ("run.bat exists", test_11),
        ("app.py has main function", test_12),
        ("app.py has chat interface", test_13),
        ("app.py has API integration", test_14),
        ("app.py has sidebar", test_15),
        ("run.bat has correct command", test_16),
        ("config.toml has theme settings", test_17),
        (".env.example has API_URL", test_18),
        ("app.py mentions COMMIT 13", test_19),
        ("app.py file is not empty", test_20),
    ]
    
    passed = 0
    failed = 0
    
    for i, (name, test_func) in enumerate(tests, 1):
        if print_test(i, name, test_func()):
            passed += 1
        else:
            failed += 1
    
    print_header(f"Resultats: {passed}/{len(tests)}")
    
    if failed == 0:
        print(f"[SUCCESS] TOUS LES TESTS COMMIT 13 SONT PASSES!")
        return 0
    else:
        print(f"[FAILED] {failed} test(s) echoue(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
