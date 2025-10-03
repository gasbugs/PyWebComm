
import socket

def get_login_page_raw():
    """Uses a raw socket to fetch the content of the login page."""
    target_host = "127.0.0.1"
    target_port = 8888

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((target_host, target_port))
        
        request = f"GET /login.php HTTP/1.1\r\nHost: {target_host}:{target_port}\r\nUser-Agent: Python-Web-Scanner/0.1\r\nConnection: close\r\n\r\n"
        
        client.send(request.encode())
        
        response_bytes = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            response_bytes += chunk

        response_string = response_bytes.decode(errors='ignore')
        
        # Split headers from body
        header_body_split = response_string.split('\r\n\r\n', 1)
        if len(header_body_split) > 1:
            return header_body_split[1] # Return only the body
        else:
            return response_string # Or original string if no body is found
        
    finally:
        client.close()

if __name__ == "__main__":
    content = get_login_page_raw()
    print(content)
