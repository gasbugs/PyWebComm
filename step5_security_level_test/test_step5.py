
import sys
import os
import pytest
import requests

# Add the project root to the path to allow importing from sibling directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Note: We are importing the scanner from the *local* step5 directory
from step4_final_scanner.scanner import scan_page_for_xss

@pytest.fixture(scope="module")
def high_security_session():
    """Pytest fixture to create a session logged in with HIGH security."""
    session = requests.Session()
    login_url = "http://127.0.0.1:8888/login.php"
    # Use security_level = 2 for this test suite
    login_payload = {"login": "bee", "password": "bug", "security_level": "2", "form": "submit"}
    
    try:
        response = session.post(login_url, data=login_payload)
        response.raise_for_status()
        if "welcome bee" not in response.text.lower():
            pytest.fail("Login failed with high security. Cannot proceed.")
        # We also need to set the cookie explicitly for some bWAPP versions
        session.cookies.set("security_level", "2", domain="127.0.0.1")
        yield session # Provide the session to the tests
    except requests.exceptions.ConnectionError as e:
        pytest.skip(f"Test SKIPPED: Connection failed. Is bWAPP running? Error: {e}")

def test_scanner_finds_no_xss_on_high_security(high_security_session):
    """
    Tests that the scanner does NOT find XSS in htmli_get.php on high security.
    Uses the high_security_session fixture.
    """
    target_url = "http://127.0.0.1:8888/htmli_get.php"
    
    # The scan_page_for_xss function returns a list of vulnerable forms found
    vulnerabilities = scan_page_for_xss(high_security_session, target_url)
    
    # Assert that NO vulnerabilities were found
    assert isinstance(vulnerabilities, list)
    assert len(vulnerabilities) == 0, "Scanner incorrectly detected a vulnerability on high security"
