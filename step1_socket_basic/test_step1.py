
# To run this test, you need to install pytest: pip install pytest
# Then run the command from the root directory: pytest 1_socket_basic/test_step1.py

import sys
import os
import pytest

# Add the parent directory to the path so we can import run_step1
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from run_step1 import get_login_page_raw

def test_get_login_page_raw():
    """
    Tests if the raw socket connection successfully retrieves the login page HTML body.
    This is a basic integration test and requires the bWAPP server to be running.
    """
    try:
        # 1. Call the function to get the page HTML body
        html_content = get_login_page_raw()
        
    except ConnectionRefusedError:
        pytest.skip("Test SKIPPED: Connection was refused. Is the bWAPP server running at 127.0.0.1:8888?")

    # 2. Assert that the content is a non-empty string
    assert isinstance(html_content, str)
    assert len(html_content) > 0
    
    # 3. Assert that it contains key elements of the bWAPP login page (case-insensitive)
    # The raw request gets a minimal HTML response, which may not have a <title> tag.
    # We will check for content that is present.
    assert "login" in html_content.lower()
    assert "bee" in html_content.lower() # Refers to the bee image/div
