
import requests
import sys
import os
from urllib.parse import urljoin

# Add the project root to the path to allow importing from sibling directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from previous steps
from step2_requests_login.run_step2 import login_and_get_page
from step3_parser_and_extract.run_step3 import extract_form_details

def submit_form_and_check_xss(session, form_details, url):
    """Submits a form with an XSS payload and checks for reflection."""
    xss_payload = '<script>alert("GEMINI_XSS_TEST")</script>'
    
    action = form_details["action"]
    method = form_details["method"]
    inputs = form_details["inputs"]
    
    # Create the data payload for submission
    data = {}
    for input_field in inputs:
        if input_field["type"] == "text":
            data[input_field["name"]] = xss_payload
        else:
            # For other input types, provide a default value
            data[input_field["name"]] = "test"
            
    # Construct the full URL for submission
    target_url = urljoin(url, action)
    
    try:
        if method == 'post':
            response = session.post(target_url, data=data)
        else: # GET method
            response = session.get(target_url, params=data)
        
        response.raise_for_status()
        
        # Check if the payload is reflected in the response
        if xss_payload in response.text:
            return True, data # Vulnerability found
            
    except requests.exceptions.RequestException as e:
        print(f"  [!] Error submitting form to {target_url}: {e}")
        
    return False, None # No vulnerability found


def scan_page_for_xss(session, url):
    """Scans a single page for XSS vulnerabilities in its forms."""
    print(f"\n[*] Scanning page: {url}")
    
    try:
        # 1. Get the page content using the authenticated session
        response = session.get(url)
        response.raise_for_status()
        
        # 2. Extract all forms from the page
        forms = extract_form_details(response.text)
        if not forms:
            print("  [-] No forms found.")
            return []

        print(f"  [*] Found {len(forms)} form(s). Testing...")
        vulnerabilities = []
        
        # 3. Test each form for XSS
        for form in forms:
            is_vulnerable, payload = submit_form_and_check_xss(session, form, url)
            if is_vulnerable:
                print(f"  [!!!] XSS VULNERABILITY FOUND in form with action: {form['action']}")
                print(f"      - Method: {form['method']}")
                print(f"      - Payload: {payload}")
                vulnerabilities.append(form)
        
        if not vulnerabilities:
            print("  [-] No XSS vulnerabilities found on this page.")
            
        return vulnerabilities

    except requests.exceptions.RequestException as e:
        print(f"[!] Could not fetch page {url}: {e}")
        return []

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="A simple XSS scanner for bWAPP.")
    parser.add_argument("--level", help="Set the bWAPP security level (0, 1, or 2)", default="0")
    args = parser.parse_args()

    print(f"--- Starting Gemini Web Scanner (Security Level: {args.level}) ---")
    
    # 1. Create a session and log in
    session = requests.Session()
    login_url = "http://127.0.0.1:8888/login.php"
    login_payload = {"login": "bee", "password": "bug", "security_level": args.level, "form": "submit"}
    
    try:
        print(f"[*] Logging in to bWAPP with security level '{args.level}'...")
        login_response = session.post(login_url, data=login_payload)
        login_response.raise_for_status()
        if "welcome bee" not in login_response.text.lower():
            raise Exception("Login Failed - check credentials or server status.")
        print("[+] Login successful!")

        # 2. Define targets and run the scan
        scan_targets = [
            "http://127.0.0.1:8888/htmli_get.php",
            "http://127.0.0.1:8888/xss_get.php", # Another vulnerable page
        ]
        
        total_vulns = 0
        for target in scan_targets:
            found = scan_page_for_xss(session, target)
            total_vulns += len(found)
            
        print("\n--- Scan Complete ---")
        print(f"Found {total_vulns} total potential vulnerabilities.")

    except Exception as e:
        print(f"[!!!] A critical error occurred: {e}")
