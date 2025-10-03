# 나만의 웹 스캐너 만들기: 최종 튜토리얼

## 소개

안녕하세요! 이 튜토리얼에서는 파이썬을 이용해 '나만의 웹 스캐너'를 만들어 봅니다. 가장 원시적인 네트워크 통신부터 시작하여, 로그인, HTML 파싱, 취약점 스캔, 그리고 서버의 방어 메커니즘 확인까지, 하나의 완전한 도구를 점진적으로 완성해 나가는 과정을 체험하게 될 것입니다.

**최종 프로젝트 구조:**
```
PyWebComm/
├── step1_socket_basic/
│   ├── run_step1.py
│   └── test_step1.py
├── step2_requests_login/
│   ├── run_step2.py
│   └── test_step2.py
├── step3_parser_and_extract/
│   ├── run_step3.py
│   └── test_step3.py
├── step4_final_scanner/
│   ├── scanner.py
│   └── test_scanner.py
├── step5_security_level_test/
│   └── test_step5.py
├── requirements.txt
└── prd.md
```

**실습 환경 정보:**
-   **타겟 서버:** `http://127.0.0.1:8888` (bWAPP/bee-box 권장)
-   **로그인 정보:** ID `bee`, PW `bug`

> **경고:** 이 튜토리얼의 모든 코드는 허가된 실습 환경 내에서만 사용해야 합니다. 허가받지 않은 시스템에 스캔을 시도하는 것은 불법 행위입니다.

---

## [1단계: 원시 소켓 통신]

### (1) 학습 목표
-   `socket` 라이브러리로 HTTP 통신의 기본 원리를 이해합니다.
-   서버 응답에서 헤더와 본문을 분리하는 방법을 학습합니다.

### (2) 코드: `step1_socket_basic/run_step1.py`
```python
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
        header_body_split = response_string.split('\r\n\r\n', 1)
        if len(header_body_split) > 1:
            return header_body_split[1]
        else:
            return response_string
    finally:
        client.close()

if __name__ == "__main__":
    content = get_login_page_raw()
    print(content)
```
- **핵심:** `User-Agent` 헤더를 추가하여 일반 클라이언트처럼 요청하고, 수신한 전체 응답에서 `\r\n\r\n`을 기준으로 헤더와 본문을 분리합니다.
- **테스트:** `step1_socket_basic/test_step1.py`는 이 스크립트가 bWAPP 서버로부터 `login`과 `bee` 문자열이 포함된 HTML 본문을 성공적으로 가져오는지 검증합니다.

---

## [2단계: `requests`를 이용한 세션 및 로그인]

### (1) 학습 목표
-   `requests` 라이브러리의 `Session` 객체로 로그인 상태를 유지하는 방법을 이해합니다.
-   POST 요청으로 폼 데이터를 전송하여 인증을 수행합니다.

### (2) 코드: `step2_requests_login/run_step2.py`
```python
import requests

def login_and_get_page(target_url):
    """Creates a session, logs into bWAPP, and fetches a target page."""
    session = requests.Session()
    login_url = "http://127.0.0.1:8888/login.php"
    login_payload = {
        "login": "bee",
        "password": "bug",
        "security_level": "0",
        "form": "submit"
    }
    session.post(login_url, data=login_payload)
    response = session.get(target_url)
    response.raise_for_status()
    return response

if __name__ == "__main__":
    page_to_fetch = "http://127.0.0.1:8888/htmli_get.php"
    try:
        final_response = login_and_get_page(page_to_fetch)
        if "welcome bee" in final_response.text.lower():
            print("[+] Login successful!")
            print(f"---\n Page Content Snippet ---\n{final_response.text[:600]}")
    except requests.exceptions.RequestException as e:
        print(f"[!] An error occurred: {e}")
```
- **핵심:** `requests.Session()` 객체가 로그인 시 서버로부터 받은 쿠키를 자동으로 저장하고, 이후의 모든 요청에 포함시켜주므로 로그인 상태가 유지됩니다.
- **테스트:** `step2_requests_login/test_step2.py`는 로그인 후 `htmli_get.php` 페이지에 접근했을 때, 응답 내용에 `welcome bee`와 `first name` 같은 문구가 포함되어 있는지 확인하여 로그인 성공 여부를 검증합니다.

---

## [3단계: `BeautifulSoup`으로 폼 정보 추출]

### (1) 학습 목표
-   `BeautifulSoup` 라이브러리로 HTML을 파싱하여 원하는 정보를 추출합니다.
-   다른 디렉토리의 파이썬 모듈을 `import`하여 재사용하는 방법을 학습합니다.

### (2) 코드: `step3_parser_and_extract/run_step3.py`
```python
import sys, os
from bs4 import BeautifulSoup
# Add project root to path to allow importing from sibling directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
            if input_tag.get('name'):
                inputs.append({"name": input_tag.get('name'), "type": input_tag.get('type', 'text')})
        extracted_data.append({"action": action, "method": method, "inputs": inputs})
    return extracted_data

if __name__ == "__main__":
    # ... (main execution logic to print form details) ...
```
- **핵심:** 2단계의 `login_and_get_page` 함수를 `import`하여 재사용하고, `BeautifulSoup(html, 'html.parser')`로 파싱 객체를 생성한 뒤, `find_all('form')`과 `find_all('input')`을 이용해 페이지 내의 모든 폼과 입력 필드 정보를 추출합니다.
- **테스트:** `step3_parser_and_extract/test_step3.py`는 페이지에 여러 폼이 존재하더라도, 우리가 원하는 `firstname` 입력 필드를 가진 폼을 정확히 찾아내고, 그 폼의 `action`, `method`, 입력 필드 이름들이 올바른지 검증합니다.

---

## [4단계: XSS 스캐너 완성 및 리팩토링]

### (1) 학습 목표
-   추출한 폼 정보에 XSS 페이로드를 삽입하여 서버에 전송하고, 응답을 분석하여 취약점을 탐지하는 로직을 완성합니다.
-   `argparse`를 사용하여 스크립트를 설정 가능한 커맨드 라인 도구로 만듭니다.

### (2) 코드: `step4_final_scanner/scanner.py`
```python
# ... (submit_form_and_check_xss, scan_page_for_xss functions) ...

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="A simple XSS scanner for bWAPP.")
    parser.add_argument("--level", help="Set the bWAPP security level (0, 1, or 2)", default="0")
    args = parser.parse_args()

    print(f"--- Starting Gemini Web Scanner (Security Level: {args.level}) ---")
    
    session = requests.Session()
    login_url = "http://127.0.0.1:8888/login.php"
    login_payload = {"login": "bee", "password": "bug", "security_level": args.level, "form": "submit"}
    
    # ... (Login and scan execution logic) ...
```
- **핵심:** `argparse`를 이용해 `--level` 옵션을 받아 `login_payload`를 동적으로 설정합니다. `submit_form_and_check_xss` 함수는 페이로드를 전송한 후, 응답 텍스트에 페이로드가 그대로 포함되어 있는지 (`if xss_payload in response.text:`) 확인하여 취약점 여부를 판단합니다.
- **테스트:** `step4_final_scanner/test_scanner.py`는 낮은 보안 레벨(`security_level=0`)로 로그인한 후 스캐너를 실행하여, `htmli_get.php`에서 실제로 XSS 취약점을 **발견하는지**를 검증합니다.

---

## [5단계: 보안 레벨을 통한 방어 메커니즘 검증]

### (1) 학습 목표
-   동일한 스캐너를 다른 설정으로 실행하여 서버 측 방어 로직을 확인합니다.
-   입력값 검증(Input Validation)과 이스케이핑(Escaping)의 중요성을 이해합니다.

### (2) 실행 방법
4단계에서 완성한 `scanner.py`를 그대로 사용하되, 커맨드 라인에서 `--level` 옵션만 `2`로 변경하여 실행합니다.

```bash
python step4_final_scanner/scanner.py --level 2
```

- **핵심:** `--level 2` 옵션으로 스캐너를 실행하면, 높은 보안 레벨로 로그인되어 bWAPP의 XSS 방어 로직이 활성화됩니다. 서버는 페이로드의 `<`나 `>` 같은 특수문자를 `&lt;`, `&gt;` 등으로 변환(이스케이핑)하여 응답합니다. 따라서 우리의 스캐너는 응답에서 원본 페이로드를 찾지 못하고, 취약점이 없다고 올바르게 판단합니다.
- **테스트:** `step5_security_level_test/test_step5.py`는 높은 보안 레벨(`security_level=2`)로 로그인한 후 스캐너를 실행하여, `htmli_get.php`에서 XSS 취약점이 **발견되지 않음**을 검증합니다.

---

## 튜토리얼 최종 마무리

축하합니다! 여러분은 5단계에 걸쳐, 원시적인 통신부터 시작하여 로그인, 파싱, 취약점 스캔, 그리고 서버의 방어 정책 검증까지 가능한, 재사용성 높고 설정 가능한 웹 스캐너를 완성했습니다. 이 과정을 통해 웹 통신, 자동화된 테스팅, 그리고 시큐어 코딩의 기본 원리까지 폭넓은 지식을 습득하셨습니다.

이 프로젝트는 여러분의 손에서 크롤러, SQL 인젝션 스캐너 등 더 강력한 도구로 발전할 수 있는 훌륭한 시작점입니다. 앞으로 더 안전한 웹을 만드는 전문가로 성장하시기를 응원합니다!