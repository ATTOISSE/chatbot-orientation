"""
Project initialization - Setup script
"""
import os
import sys

def verify_structure():
    """Verify project structure"""
    print("🔍 Verifying project structure...")
    
    dirs_to_check = [
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
    
    files_to_check = [
        '.gitignore',
        '.env.example',
        'README.md',
        'backend/app/main.py',
        'datas/formations.json',
        'datas/ecoles.json',
        'datas/anaq_accreditations.json'
    ]
    
    missing = []
    
    for d in dirs_to_check:
        if not os.path.isdir(d):
            missing.append(f"❌ Missing directory: {d}")
    
    for f in files_to_check:
        if not os.path.isfile(f):
            missing.append(f"❌ Missing file: {f}")
    
    if missing:
        print("\n".join(missing))
        return False
    
    print("✅ All directories and files present!")
    return True

def main():
    print("=" * 60)
    print("🚀 EduGuide Sénégal - Project Initialization")
    print("=" * 60)
    
    if verify_structure():
        print("\n✅ Project structure is ready!")
        print("\nNext steps:")
        print("1. Review .env.example and create .env file")
        print("2. Install backend dependencies: pip install -r backend/requirements.txt")
        print("3. Install frontend dependencies: pip install -r frontend/requirements.txt")
        print("4. Run tests: pytest tests/test_init.py")
        print("5. Start services: docker-compose up --build")
        return 0
    else:
        print("\n❌ Project structure incomplete!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
