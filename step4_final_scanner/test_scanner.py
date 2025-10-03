
import sys
import os
import pytest
import requests

# Add the project root to the path to allow importing from sibling directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from step4_final_scanner.scanner import scan_page_for_xss

@pytest.fixture(scope="module")
def authenticated_session():
    """Pytest fixture to create a logged-in session once for all tests in this module."""
    session = requests.Session()
    login_url = "http://127.0.0.1:8888/login.php"
    login_payload = {"login": "bee", "password": "bug", "security_level": "0", "form": "submit"}
    
    try:
        response = session.post(login_url, data=login_payload)
        response.raise_for_status()
        if "welcome bee" not in response.text.lower():
            pytest.fail("Login failed. Cannot proceed with authenticated tests.")
        yield session # Provide the session to the tests
    except requests.exceptions.ConnectionError as e:
        pytest.skip(f"Test SKIPPED: Connection failed. Is bWAPP running? Error: {e}")

def test_scanner_finds_xss_in_htmli_get(authenticated_session):
    """
    Tests if the scanner correctly identifies the XSS vulnerability in htmli_get.php.
    Uses the authenticated_session fixture.
    """
    vulnerable_url = "http://127.0.0.1:8888/htmli_get.php"
    
    # The scan_page_for_xss function returns a list of vulnerable forms found
    vulnerabilities = scan_page_for_xss(authenticated_session, vulnerable_url)
    
    # Assert that at least one vulnerability was found on this page
    assert vulnerabilities is not None
    assert len(vulnerabilities) > 0, "Scanner did not detect the known XSS vulnerability in htmli_get.php"
    
    # Optional: More detailed check on the found vulnerability
    vuln_form = vulnerabilities[0]
    assert vuln_form['action'] == '/htmli_get.php'
    assert vuln_form['method'] == 'get'
