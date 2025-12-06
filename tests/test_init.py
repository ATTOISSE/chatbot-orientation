"""
Test file to verify project structure
Run with: pytest tests/test_init.py
"""
import os
import json


def test_directory_structure():
    """Test that all required directories exist"""
    required_dirs = [
        'backend/app',
        'backend/app/auth',
        'backend/app/api/routes',
        'backend/app/models',
        'backend/app/services',
        'backend/app/database',
        'backend/app/rag',
        'backend/app/utils',
        'frontend',
        'frontend/pages',
        'frontend/components',
        'scripts',
        'tests',
        'datas'
    ]
    
    for dir_path in required_dirs:
        assert os.path.isdir(dir_path), f"Missing directory: {dir_path}"
    
    print("✅ All required directories exist!")


def test_file_structure():
    """Test that key files exist"""
    required_files = [
        '.gitignore',
        '.env.example',
        'README.md',
        'backend/app/main.py',
        'backend/app/__init__.py',
        'frontend/__init__.py',
    ]
    
    for file_path in required_files:
        assert os.path.isfile(file_path), f"Missing file: {file_path}"
    
    print("✅ All required files exist!")


def test_env_example_format():
    """Test that .env.example is properly formatted"""
    with open('.env.example', 'r') as f:
        content = f.read()
        assert 'DATABASE_URL' in content
        assert 'JWT_SECRET' in content
        assert 'HUGGINGFACE_API_KEY' in content
        assert 'CHROMADB' in content
    
    print("✅ .env.example properly formatted!")


def test_readme_exists():
    """Test that README.md has essential content"""
    with open('README.md', 'r') as f:
        content = f.read()
        assert 'EduGuide' in content
        assert 'FastAPI' in content
        assert 'Streamlit' in content
    
    print("✅ README.md contains essential content!")


def test_data_files_exist():
    """Test that data JSON files exist"""
    data_files = [
        'datas/formations.json',
        'datas/ecoles.json',
        'datas/anaq_accreditations.json'
    ]
    
    for file_path in data_files:
        assert os.path.isfile(file_path), f"Missing data file: {file_path}"
    
    # Verify they are valid JSON
    for file_path in data_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                json.load(f)
                print(f"✅ {file_path} is valid JSON!")
            except json.JSONDecodeError as e:
                raise AssertionError(f"Invalid JSON in {file_path}: {e}")


if __name__ == '__main__':
    print("🧪 Running initialization tests...\n")
    test_directory_structure()
    test_file_structure()
    test_env_example_format()
    test_readme_exists()
    test_data_files_exist()
    print("\n✅ All tests passed! Project structure is ready.")
