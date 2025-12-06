#!/usr/bin/env python3
"""
COMMIT 7: Validation complète - Search Endpoints
Test de validation des endpoints de recherche sophistiquée

Tests:
1. Endpoint /search/formations existe
2. Recherche par texte fonctionne
3. Filtrage par domaine fonctionne
4. Filtrage par établissement fonctionne
5. Filtrage par ville fonctionne
6. Filtrage par prix fonctionne
7. Filtrage par niveau fonctionne
8. Filtrage par type de formation fonctionne
9. Pagination fonctionne
10. Tri fonctionne
11. Endpoint /search/domaines fonctionne
12. Endpoint /search/etablissements fonctionne
13. Endpoint /search/stats fonctionne
"""

import requests
from pathlib import Path
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
SEARCH_ENDPOINT = f"{BASE_URL}/api/v1/search"

# Couleurs
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


class TestValidator:
    """Validateur pour COMMIT 7"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def print_test(self, name, status, message=""):
        """Affiche un résultat de test"""
        if status:
            print(f"{Colors.GREEN}✅ {name}{Colors.RESET}")
            self.passed += 1
        else:
            print(f"{Colors.RED}❌ {name}{Colors.RESET}")
            if message:
                print(f"   {Colors.YELLOW}→ {message}{Colors.RESET}")
            self.failed += 1
    
    def test_endpoint_exists(self):
        """Test 1: Endpoint /search/formations existe"""
        try:
            response = requests.post(
                f"{SEARCH_ENDPOINT}/formations",
                json={"q": "test"},
                timeout=5
            )
            
            valid = response.status_code == 200
            self.print_test(
                "Test 1: Endpoint /search/formations",
                valid,
                f"status: {response.status_code}" if not valid else ""
            )
        except Exception as e:
            self.print_test("Test 1: Endpoint /search/formations", False, str(e))
    
    def test_text_search(self):
        """Test 2: Recherche par texte"""
        try:
            response = requests.post(
                f"{SEARCH_ENDPOINT}/formations",
                json={"q": "informatique"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                valid = "items" in data and "total" in data
                self.print_test("Test 2: Recherche par texte", valid)
            else:
                self.print_test("Test 2: Recherche par texte", False, f"status: {response.status_code}")
        except Exception as e:
            self.print_test("Test 2: Recherche par texte", False, str(e))
    
    def test_filter_domaine(self):
        """Test 3: Filtrage par domaine"""
        try:
            # D'abord, récupérer les domaines
            response_domaines = requests.get(f"{SEARCH_ENDPOINT}/domaines", timeout=5)
            
            if response_domaines.status_code == 200:
                domaines = response_domaines.json()
                if domaines:
                    domaine_id = domaines[0]["id"]
                    
                    # Rechercher par domaine
                    response = requests.post(
                        f"{SEARCH_ENDPOINT}/formations",
                        json={"domaine_id": domaine_id},
                        timeout=5
                    )
                    
                    valid = response.status_code == 200
                    self.print_test("Test 3: Filtrage par domaine", valid)
                else:
                    self.print_test("Test 3: Filtrage par domaine", False, "No domaines found")
            else:
                self.print_test("Test 3: Filtrage par domaine", False, "Cannot fetch domaines")
        except Exception as e:
            self.print_test("Test 3: Filtrage par domaine", False, str(e))
    
    def test_filter_etablissement(self):
        """Test 4: Filtrage par établissement"""
        try:
            # D'abord, récupérer les établissements
            response_etab = requests.get(f"{SEARCH_ENDPOINT}/etablissements", timeout=5)
            
            if response_etab.status_code == 200:
                etablissements = response_etab.json()
                if etablissements:
                    etab_id = etablissements[0]["id"]
                    
                    # Rechercher par établissement
                    response = requests.post(
                        f"{SEARCH_ENDPOINT}/formations",
                        json={"etablissement_id": etab_id},
                        timeout=5
                    )
                    
                    valid = response.status_code == 200
                    self.print_test("Test 4: Filtrage par établissement", valid)
                else:
                    self.print_test("Test 4: Filtrage par établissement", False, "No établissements found")
            else:
                self.print_test("Test 4: Filtrage par établissement", False, "Cannot fetch établissements")
        except Exception as e:
            self.print_test("Test 4: Filtrage par établissement", False, str(e))
    
    def test_filter_ville(self):
        """Test 5: Filtrage par ville"""
        try:
            # D'abord, récupérer les villes
            response_villes = requests.get(f"{SEARCH_ENDPOINT}/villes", timeout=5)
            
            if response_villes.status_code == 200:
                villes = response_villes.json()
                if villes:
                    ville = villes[0]["ville"]
                    
                    # Rechercher par ville
                    response = requests.post(
                        f"{SEARCH_ENDPOINT}/formations",
                        json={"ville": ville},
                        timeout=5
                    )
                    
                    valid = response.status_code == 200
                    self.print_test("Test 5: Filtrage par ville", valid)
                else:
                    self.print_test("Test 5: Filtrage par ville", False, "No villes found")
            else:
                self.print_test("Test 5: Filtrage par ville", False, "Cannot fetch villes")
        except Exception as e:
            self.print_test("Test 5: Filtrage par ville", False, str(e))
    
    def test_filter_price(self):
        """Test 6: Filtrage par prix"""
        try:
            response = requests.post(
                f"{SEARCH_ENDPOINT}/formations",
                json={
                    "cost_min": 0,
                    "cost_max": 5000000
                },
                timeout=5
            )
            
            valid = response.status_code == 200
            self.print_test("Test 6: Filtrage par prix", valid)
        except Exception as e:
            self.print_test("Test 6: Filtrage par prix", False, str(e))
    
    def test_filter_niveau(self):
        """Test 7: Filtrage par niveau"""
        try:
            response = requests.post(
                f"{SEARCH_ENDPOINT}/formations",
                json={"niveau": "L3"},
                timeout=5
            )
            
            valid = response.status_code == 200
            self.print_test("Test 7: Filtrage par niveau", valid)
        except Exception as e:
            self.print_test("Test 7: Filtrage par niveau", False, str(e))
    
    def test_filter_type(self):
        """Test 8: Filtrage par type de formation"""
        try:
            response = requests.post(
                f"{SEARCH_ENDPOINT}/formations",
                json={"type_formation": "Licence"},
                timeout=5
            )
            
            valid = response.status_code == 200
            self.print_test("Test 8: Filtrage par type", valid)
        except Exception as e:
            self.print_test("Test 8: Filtrage par type", False, str(e))
    
    def test_pagination(self):
        """Test 9: Pagination"""
        try:
            response = requests.post(
                f"{SEARCH_ENDPOINT}/formations",
                json={"page": 1, "page_size": 10},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                has_pagination = all(k in data for k in ["page", "page_size", "total_pages"])
                self.print_test("Test 9: Pagination", has_pagination)
            else:
                self.print_test("Test 9: Pagination", False, f"status: {response.status_code}")
        except Exception as e:
            self.print_test("Test 9: Pagination", False, str(e))
    
    def test_sorting(self):
        """Test 10: Tri"""
        try:
            response = requests.post(
                f"{SEARCH_ENDPOINT}/formations",
                json={"sort_by": "cost_asc", "page": 1, "page_size": 20},
                timeout=5
            )
            
            valid = response.status_code == 200
            self.print_test("Test 10: Tri", valid)
        except Exception as e:
            self.print_test("Test 10: Tri", False, str(e))
    
    def test_list_domaines(self):
        """Test 11: Endpoint /search/domaines"""
        try:
            response = requests.get(f"{SEARCH_ENDPOINT}/domaines", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                valid = isinstance(data, list) and len(data) > 0
                self.print_test(
                    "Test 11: Endpoint /search/domaines",
                    valid,
                    f"found {len(data)} domaines" if valid else "empty list"
                )
            else:
                self.print_test("Test 11: Endpoint /search/domaines", False, f"status: {response.status_code}")
        except Exception as e:
            self.print_test("Test 11: Endpoint /search/domaines", False, str(e))
    
    def test_list_etablissements(self):
        """Test 12: Endpoint /search/etablissements"""
        try:
            response = requests.get(f"{SEARCH_ENDPOINT}/etablissements", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                valid = isinstance(data, list) and len(data) > 0
                self.print_test(
                    "Test 12: Endpoint /search/etablissements",
                    valid,
                    f"found {len(data)} établissements" if valid else "empty list"
                )
            else:
                self.print_test("Test 12: Endpoint /search/etablissements", False, f"status: {response.status_code}")
        except Exception as e:
            self.print_test("Test 12: Endpoint /search/etablissements", False, str(e))
    
    def test_stats(self):
        """Test 13: Endpoint /search/stats"""
        try:
            response = requests.get(f"{SEARCH_ENDPOINT}/stats", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                has_stats = all(k in data for k in ["total_formations", "total_domaines", "total_etablissements"])
                self.print_test("Test 13: Endpoint /search/stats", has_stats)
            else:
                self.print_test("Test 13: Endpoint /search/stats", False, f"status: {response.status_code}")
        except Exception as e:
            self.print_test("Test 13: Endpoint /search/stats", False, str(e))
    
    def run_all(self):
        """Exécute tous les tests"""
        print("\n" + "="*70)
        print("  COMMIT 7: VALIDATION - SEARCH ENDPOINTS")
        print("  Recherche sophistiquée de formations avec filtres avancés")
        print("="*70 + "\n")
        
        self.test_endpoint_exists()
        self.test_text_search()
        self.test_filter_domaine()
        self.test_filter_etablissement()
        self.test_filter_ville()
        self.test_filter_price()
        self.test_filter_niveau()
        self.test_filter_type()
        self.test_pagination()
        self.test_sorting()
        self.test_list_domaines()
        self.test_list_etablissements()
        self.test_stats()
        
        print("\n" + "="*70)
        print(f"  {Colors.BLUE}Résultats: {self.passed} ✓  {self.failed} ✗{Colors.RESET}")
        print("="*70 + "\n")
        
        if self.failed == 0:
            print(f"{Colors.GREEN}✅ TOUS LES TESTS COMMIT 7 SONT PASSÉS!{Colors.RESET}\n")
            return 0
        else:
            print(f"{Colors.RED}❌ {self.failed} TEST(S) ÉCHOUÉ(S){Colors.RESET}\n")
            return 1


if __name__ == "__main__":
    validator = TestValidator()
    exit_code = validator.run_all()
    sys.exit(exit_code)
