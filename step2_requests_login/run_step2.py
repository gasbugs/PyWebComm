
import requests

def login_and_get_page(target_url):
    """
    Creates a session, logs into bWAPP, and fetches a target page.
    Returns the final response object from the target page.
    """
    session = requests.Session()

    login_url = "http://127.0.0.1:8888/login.php"
    login_payload = {
        "login": "bee",
        "password": "bug",
        "security_level": "0",
        "form": "submit"
    }

    # 1. Log in to the application
    # We don't check the response here, we'll verify success by accessing a protected page
    session.post(login_url, data=login_payload)

    # 2. Access the target page with the authenticated session
    response = session.get(target_url)
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    
    return response

if __name__ == "__main__":
    # The page we want to access after logging in
    page_to_fetch = "http://127.0.0.1:8888/htmli_get.php"
    
    try:
        print(f"[*] Logging in and attempting to fetch {page_to_fetch}")
        final_response = login_and_get_page(page_to_fetch)
        
        # Check if login was successful by looking for a keyword
        if "welcome bee" in final_response.text.lower():
            print("[+] Login successful!")
            print(f"[*] Successfully fetched page: {final_response.url}")
            print(f"--- Page Content Snippet ---")
            print(final_response.text[:600])
        else:
            # This case might happen if the login payload is wrong, 
            # or if the welcome message changes.
            print("[!] Login might have failed. 'Welcome bee' not found.")
            print(f"--- Page Content Snippet ---")
            print(final_response.text[:600])

    except requests.exceptions.RequestException as e:
        print(f"[!] An error occurred: {e}")
        print("[!] Is the bWAPP server running at http://127.0.0.1:8888?")
