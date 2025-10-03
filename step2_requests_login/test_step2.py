
import sys
import os
import pytest
import requests

# Add the parent directory to the path so we can import run_step2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from run_step2 import login_and_get_page

def test_login_and_get_page():
    """
    Tests if the login is successful and the target page is retrieved.
    Requires the bWAPP server to be running.
    """
    target_page = "http://127.0.0.1:8888/htmli_get.php"

    try:
        # 1. Call the function to log in and get the page
        response = login_and_get_page(target_page)

    except requests.exceptions.ConnectionError:
        pytest.skip("Test SKIPPED: Connection failed. Is the bWAPP server running at http://127.0.0.1:8888?")

    # 2. Assert that the request was successful
    assert response.status_code == 200

    # 3. Assert that the login was successful by checking for a welcome message
    # This message appears on all pages after login in bWAPP
    assert "welcome bee" in response.text.lower()

    # 4. Assert that we landed on the correct page
    assert "htmli_get.php" in response.url
    assert "first name" in response.text.lower()
    assert "last name" in response.text.lower()
