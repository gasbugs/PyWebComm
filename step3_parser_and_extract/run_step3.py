
import sys
import os
from bs4 import BeautifulSoup
import requests

# Add the project root to the path to allow importing from sibling directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the login function from Step 2
from step2_requests_login.run_step2 import login_and_get_page

def extract_form_details(html_content):
    """Parses HTML to find all forms and extracts their details."""
    soup = BeautifulSoup(html_content, 'html.parser')
    forms = soup.find_all('form')
    
    extracted_data = []
    
    for form in forms:
        action = form.get('action')
        method = form.get('method', 'get').lower()
        
        inputs = []
        for input_tag in form.find_all('input'):
            input_name = input_tag.get('name')
            input_type = input_tag.get('type', 'text')
            if input_name:
                inputs.append({"name": input_name, "type": input_type})
        
        extracted_data.append({
            "action": action,
            "method": method,
            "inputs": inputs
        })
        
    return extracted_data

if __name__ == "__main__":
    page_to_parse = "http://127.0.0.1:8888/htmli_get.php"
    
    try:
        print(f"[*] Logging in and fetching page: {page_to_parse}")
        response = login_and_get_page(page_to_parse)
        
        print("[*] Page fetched successfully. Now parsing for forms...")
        forms_data = extract_form_details(response.text)
        
        if not forms_data:
            print("[-] No forms found on the page.")
        else:
            print(f"[+] Found {len(forms_data)} form(s).")
            for i, form_data in enumerate(forms_data, 1):
                print(f"--- Form #{i} ---")
                print(f"  Action: {form_data['action']}")
                print(f"  Method: {form_data['method']}")
                print(f"  Inputs: {len(form_data['inputs'])}")
                for input_field in form_data['inputs']:
                    print(f"    - Name: {input_field['name']}, Type: {input_field['type']}")

    except requests.exceptions.RequestException as e:
        print(f"[!] An error occurred: {e}")
