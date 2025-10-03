
import sys
import os
import pytest
import requests

# Add the project root to the path to allow importing from sibling directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from step2_requests_login.run_step2 import login_and_get_page
from step3_parser_and_extract.run_step3 import extract_form_details

def test_extract_form_details():
    """
    Tests if the form details are correctly extracted from the target page.
    Requires the bWAPP server to be running.
    """
    target_page = "http://127.0.0.1:8888/htmli_get.php"

    try:
        # 1. Log in and get the page content
        response = login_and_get_page(target_page)
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Test SKIPPED: Connection failed. Is the bWAPP server running at http://127.0.0.1:8888?")

    # 2. Extract form details from the HTML
    forms_data = extract_form_details(response.text)

    # 3. Assert that the form data is correct
    assert isinstance(forms_data, list)
    assert len(forms_data) > 0, "Expected to find at least one form"

    # Find the specific form we want to test (the one with the 'firstname' input)
    target_form = None
    for form in forms_data:
        input_names = {input_field['name'] for input_field in form['inputs']}
        if "firstname" in input_names:
            target_form = form
            break
    
    assert target_form is not None, "Could not find the target form with 'firstname' input"

    # 4. Assert the details of the specific form
    assert target_form['method'] == 'get'
    assert target_form['action'] == '/htmli_get.php'
    
    target_input_names = {input_field['name'] for input_field in target_form['inputs']}
    expected_input_names = {"firstname", "lastname"}
    assert target_input_names == expected_input_names, f"Expected inputs {expected_input_names}, but got {target_input_names}"
