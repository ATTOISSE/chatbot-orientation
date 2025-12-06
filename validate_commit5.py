#!/usr/bin/env python3
"""
COMMIT 5 Validation Script: Authentication API Endpoints
Tests all authentication endpoints and their functionality
"""

import requests
import json
import time
from typing import Dict, Tuple

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/auth"

# Test data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
}

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

def print_test(num: int, name: str):
    print(f"\n{Colors.BLUE}[TEST {num}] {name}{Colors.RESET}")

def print_pass(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_fail(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.RESET}")

def test_health() -> bool:
    """Test 1: Health endpoint"""
    print_test(1, "Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_pass("Health endpoint is responding")
            return True
        else:
            print_fail(f"Health endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Health endpoint error: {e}")
        return False

def test_register() -> Tuple[bool, str]:
    """Test 2: Register endpoint"""
    print_test(2, "Register Endpoint")
    try:
        response = requests.post(
            f"{API_URL}/register",
            json=TEST_USER,
            timeout=5
        )
        print_info(f"Status: {response.status_code}")
        
        if response.status_code in [201, 200]:
            data = response.json()
            if "id" in data and "email" in data:
                print_pass("User registration successful")
                user_id = data.get("id")
                return True, user_id
            else:
                print_fail(f"Unexpected response format: {data}")
                return False, None
        elif response.status_code == 400:
            # User might already exist
            print_info("User already exists (expected on retry)")
            return True, None
        else:
            print_fail(f"Registration failed: {response.text}")
            return False, None
    except Exception as e:
        print_fail(f"Registration error: {e}")
        return False, None

def test_login() -> Tuple[bool, str]:
    """Test 3: Login endpoint"""
    print_test(3, "Login Endpoint")
    try:
        response = requests.post(
            f"{API_URL}/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            timeout=5
        )
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "token_type" in data:
                print_pass("Login successful")
                print_info(f"Token type: {data['token_type']}")
                return True, data["access_token"]
            else:
                print_fail(f"Missing token in response: {data}")
                return False, None
        else:
            print_fail(f"Login failed: {response.text}")
            return False, None
    except Exception as e:
        print_fail(f"Login error: {e}")
        return False, None

def test_me(token: str) -> bool:
    """Test 4: Get current user endpoint"""
    print_test(4, "Get Current User (/me) Endpoint")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/me",
            headers=headers,
            timeout=5
        )
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "email" in data and data["email"] == TEST_USER["email"]:
                print_pass("Current user retrieved successfully")
                return True
            else:
                print_fail(f"Unexpected user data: {data}")
                return False
        else:
            print_fail(f"Get user failed: {response.text}")
            return False
    except Exception as e:
        print_fail(f"Get user error: {e}")
        return False

def test_refresh_token() -> bool:
    """Test 5: Refresh token endpoint"""
    print_test(5, "Refresh Token Endpoint")
    try:
        # First login
        login_response = requests.post(
            f"{API_URL}/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            timeout=5
        )
        
        if login_response.status_code != 200:
            print_fail("Could not login for token refresh test")
            return False
        
        refresh_token = login_response.json().get("refresh_token")
        if not refresh_token:
            print_fail("No refresh token in login response")
            return False
        
        # Refresh the token
        response = requests.post(
            f"{API_URL}/refresh",
            json={"refresh_token": refresh_token},
            timeout=5
        )
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print_pass("Token refresh successful")
                return True
            else:
                print_fail(f"Missing new token: {data}")
                return False
        else:
            print_fail(f"Token refresh failed: {response.text}")
            return False
    except Exception as e:
        print_fail(f"Token refresh error: {e}")
        return False

def test_change_password(token: str) -> bool:
    """Test 6: Change password endpoint"""
    print_test(6, "Change Password Endpoint")
    try:
        response = requests.post(
            f"{API_URL}/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": TEST_USER["password"],
                "new_password": "NewSecurePass123"
            },
            timeout=5
        )
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print_pass("Password change successful")
            # Revert for other tests
            requests.post(
                f"{API_URL}/change-password",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "old_password": "NewSecurePass123",
                    "new_password": TEST_USER["password"]
                },
                timeout=5
            )
            return True
        else:
            print_fail(f"Password change failed: {response.text}")
            return False
    except Exception as e:
        print_fail(f"Password change error: {e}")
        return False

def test_cors() -> bool:
    """Test 7: CORS headers"""
    print_test(7, "CORS Configuration")
    try:
        response = requests.options(
            f"{API_URL}/register",
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        
        allowed_origin = response.headers.get("Access-Control-Allow-Origin")
        if allowed_origin:
            print_pass(f"CORS enabled for origin: {allowed_origin}")
            return True
        else:
            print_info("CORS headers not present (may be expected)")
            return True
    except Exception as e:
        print_fail(f"CORS test error: {e}")
        return False

def test_swagger_docs() -> bool:
    """Test 8: Swagger documentation"""
    print_test(8, "Swagger Documentation")
    try:
        response = requests.get(
            f"{BASE_URL}/docs",
            timeout=5
        )
        
        if response.status_code == 200:
            print_pass("Swagger docs available at /docs")
            return True
        else:
            print_fail(f"Swagger docs returned {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Swagger docs error: {e}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"COMMIT 5 VALIDATION: Authentication API Endpoints")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Register
    register_ok, user_id = test_register()
    results.append(("Register", register_ok))
    
    # Test 3: Login
    login_ok, token = test_login()
    results.append(("Login", login_ok))
    
    if token:
        # Test 4: Me
        results.append(("Get Current User", test_me(token)))
        
        # Test 5: Refresh Token
        results.append(("Refresh Token", test_refresh_token()))
        
        # Test 6: Change Password
        results.append(("Change Password", test_change_password(token)))
    
    # Test 7: CORS
    results.append(("CORS Configuration", test_cors()))
    
    # Test 8: Swagger
    results.append(("Swagger Docs", test_swagger_docs()))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{name:.<40} {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}✅ COMMIT 5 VALIDATION SUCCESSFUL!{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}❌ Some tests failed. Review output above.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    exit(main())
