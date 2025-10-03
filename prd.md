# 나만의 웹 스캐너 만들기: 실전 튜토리얼 (bWAPP 환경)

## 소개

안녕하세요! 파이썬과 정보 보안을 가르치는 전문 강사입니다. 이 튜토리얼에서는 여러분과 함께 **실제 동작하는 취약한 웹 환경(bWAPP)**을 대상으로 '나만의 웹 스캐너'를 만들어 보겠습니다. 가장 원시적인 네트워크 통신에서 시작하여, 로그인 처리, 취약점 페이로드 전송까지, 코드를 점진적으로 '진화'시키는 과정을 직접 체험하게 될 것입니다. 이 과정을 통해 여러분은 웹 통신의 기본 원리와 보안 스캐너의 핵심 로직을 실감 나게 이해하게 될 것입니다.

**실습 환경 정보:**
-   **타겟 서버:** `http://127.0.0.1:8888`
-   **로그인 페이지:** `http://127.0.0.1:8888/login.php`
-   **로그인 정보:** ID `bee`, PW `bug`
-   **테스트 페이지:** `http://127.0.0.1:8888/htmli_get.php`

> **경고:** 이 튜토리얼의 모든 코드는 허가된 실습 환경(bWAPP/bee-box) 내에서만 사용해야 합니다. 허가받지 않은 시스템에 스캔을 시도하는 것은 불법 행위입니다.

---

## [1단계: 소켓(Socket)을 이용한 원시적인 접근]

### (1) 학습 목표
-   HTTP 프로토콜이 사실은 정해진 양식의 텍스트(Plain Text)라는 것을 이해합니다.
-   파이썬의 `socket` 라이브러리를 이용해 로컬 웹 서버와 직접 통신하는 원리를 학습합니다.

### (2) 전체 파이썬 코드

```python
import socket

# 접속할 서버 정보 (로컬 bWAPP 환경)
target_host = "127.0.0.1"
target_port = 8888

# 1. 소켓 객체 생성
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 서버에 연결
client.connect((target_host, target_port))

# 3. HTTP 요청 메시지 생성 (로그인 페이지 요청)
# Host 헤더에 포트 번호까지 명시해야 할 수 있습니다.
request = f"GET /login.php HTTP/1.1
Host: {target_host}:{target_port}
Connection: close

"

# 4. 요청 메시지 전송
client.send(request.encode())

# 5. 서버로부터 응답 수신
response = b""
while True:
    chunk = client.recv(4096)
    if not chunk:
        break
    response += chunk

# 6. 응답 출력
print(response.decode(errors='ignore'))

# 7. 소켓 닫기
client.close()
```

### (3) 상세한 코드 설명
-   **`target_host`, `target_port`**: 실습 환경인 `127.0.0.1`과 `8888` 포트로 변경했습니다.
-   **`request = ...`**: `GET /login.php ...` 로 변경하여, 서버의 루트가 아닌 로그인 페이지를 직접 요청합니다. `Host` 헤더에는 가상 호스팅 환경을 위해 포트 번호까지 포함하는 것이 안정적입니다. `Connection: close` 헤더는 요청 처리 후 서버가 연결을 바로 끊도록 하여, 응답 수신 루프가 깔끔하게 종료되도록 합니다.
-   나머지 로직은 이전과 동일합니다. 이 코드를 실행하면 `login.php` 페이지의 HTML 코드가 그대로 출력되는 것을 볼 수 있습니다.

### (4) 이 코드의 한계점과 다음 단계의 필요성
1단계의 한계는 더욱 명확해졌습니다. 우리는 로그인 페이지의 HTML을 받아왔을 뿐, 로그인을 '수행'하지는 못했습니다. 로그인을 하려면 아이디와 비밀번호를 서버에 보내고, 서버가 발급해주는 '로그인 상태 유지용 쿠키(Cookie)'를 저장했다가 다음 요청부터 계속 사용해야 합니다. 소켓만으로 이 모든 과정을 구현하는 것은 매우 복잡합니다. 이 과정을 자동으로 처리해주는 `requests` 라이브러리의 필요성이 더욱 절실해집니다.

---

## [2단계: requests 라이브러리로 로그인 처리하기]

### (1) 학습 목표
-   `requests` 라이브러리의 세션(Session) 기능을 이용해 로그인 상태를 유지하는 방법을 이해합니다.
-   POST 방식으로 폼 데이터를 서버에 전송하여 로그인을 수행하는 방법을 학습합니다.

### (2) 전체 파이썬 코드

#### 라이브러리 설치
```bash
pip install requests
```

#### 파이썬 코드
```python
import requests

# 세션 객체 생성: 쿠키 등 로그인 정보를 자동으로 관리
session = requests.Session()

# 로그인 페이지 URL
login_url = "http://127.0.0.1:8888/login.php"

# 전송할 로그인 데이터 (bWAPP의 로그인 폼 구조에 맞춤)
login_payload = {
    "login": "bee",
    "password": "bug",
    "security_level": "0", # bWAPP 보안 레벨
    "form": "submit"
}

try:
    # 1. POST 요청으로 로그인 시도
    print("[*] Logging in...")
    login_response = session.post(login_url, data=login_payload)
    login_response.raise_for_status()

    # 로그인 성공 여부 확인 (로그인 후 보이는 문구로 판단)
    if "Welcome bee" not in login_response.text:
        print("[!] Login failed!")
    else:
        print("[+] Login successful!")

        # 2. 로그인 상태에서만 접근 가능한 페이지 요청
        target_page_url = "http://127.0.0.1:8888/htmli_get.php"
        print(f"[*] Accessing {target_page_url}")
        target_response = session.get(target_page_url)
        target_response.raise_for_status()
        
        print(f"--- Status Code: {target_response.status_code} ---")
        # 페이지 내용의 일부만 출력하여 확인
        print(target_response.text[:500])

except requests.exceptions.RequestException as e:
    print(f"[!] Error: {e}")
```

### (3) 상세한 코드 설명
1.  **`session = requests.Session()`**: 일반 `requests` 대신 `Session` 객체를 생성합니다. 이 객체를 통해 이뤄지는 모든 통신은 쿠키가 자동으로 공유되어, 한번 로그인하면 세션이 유지되는 효과를 냅니다.
2.  **`login_payload`**: bWAPP 로그인 폼의 `<input>` 태그들을 분석하여 만든 딕셔너리입니다. `name="login"`, `name="password"` 등의 속성에 맞춰 `bee`와 `bug` 값을 설정합니다.
3.  **`session.post(login_url, data=login_payload)`**: `GET`이 아닌 `POST` 방식으로, `data` 인자에 `login_payload`를 담아 전송합니다. 이것이 바로 폼을 채워 '제출'하는 행위에 해당합니다.
4.  **`session.get(target_page_url)`**: **로그인에 성공한 `session` 객체를 그대로 사용**하여 다른 페이지를 요청합니다. `session`이 로그인 쿠키를 기억하고 있다가 요청 헤더에 자동으로 포함시켜주므로, 서버는 우리가 로그인한 사용자임을 인지하고 페이지를 보여줍니다.

### (4) 이 코드의 한계점과 다음 단계의 필요성
로그인에 성공하고, 원하는 페이지의 HTML을 가져오는 데 성공했습니다. 하지만 여전히 `target_response.text`는 거대한 문자열 덩어리입니다. `htmli_get.php` 페이지에 있는 XSS 테스트용 폼(form)을 찾고, 그 안에 있는 입력 필드(firstname, lastname)의 이름을 알아내려면 이 HTML을 체계적으로 분석해야 합니다. `BeautifulSoup`의 역할이 바로 여기에 있습니다.

---

## [3단계: BeautifulSoup으로 취약한 폼(Form) 분석하기]

### (1) 학습 목표
-   로그인된 세션을 유지하며 가져온 HTML을 `BeautifulSoup`으로 파싱하는 방법을 학습합니다.
-   타겟 페이지(`htmli_get.php`)의 폼 구조를 분석하여 스캔에 필요한 정보를 추출합니다.

### (2) 전체 파이썬 코드

#### 라이브러리 설치
```bash
pip install beautifulsoup4
```

#### 파이썬 코드
```python
import requests
from bs4 import BeautifulSoup

# --- 2단계의 로그인 코드와 동일 ---
session = requests.Session()
login_url = "http://127.0.0.1:8888/login.php"
login_payload = {
    "login": "bee", "password": "bug",
    "security_level": "0", "form": "submit"
}

try:
    print("[*] Logging in...")
    login_response = session.post(login_url, data=login_payload)
    login_response.raise_for_status()
    if "Welcome bee" not in login_response.text: raise Exception("Login Failed")
    print("[+] Login successful!")
    # ----------------------------------

    # 1. XSS 테스트 페이지 접속 및 파싱
    target_url = "http://127.0.0.1:8888/htmli_get.php"
    print(f"[*] Fetching and parsing {target_url}")
    response = session.get(target_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. 페이지의 모든 폼 찾기 (이 페이지엔 1개)
    forms = soup.find_all('form')
    print(f"[*] Found {len(forms)} forms.")

    for form in forms:
        # 3. 폼의 속성 정보 추출
        action = form.get('action')
        method = form.get('method', 'get').lower()
        print(f"  - Form action: '{action}', method: '{method}'")

        # 4. 폼 내부의 입력 필드 정보 추출
        inputs = form.find_all('input')
        input_names = [input_tag.get('name') for input_tag in inputs if input_tag.get('name')]
        print(f"  - Found input fields: {input_names}")

except Exception as e:
    print(f"[!] Error: {e}")

```

### (3) 상세한 코드 설명
1.  **로그인 로직**: 2단계의 로그인 코드를 그대로 사용하여 `session`을 인증된 상태로 만듭니다.
2.  **`session.get(target_url)`**: 인증된 `session`으로 `htmli_get.php` 페이지의 내용을 가져옵니다.
3.  **`soup = BeautifulSoup(...)`**: 가져온 HTML을 파싱하여 `soup` 객체를 만듭니다.
4.  **`form.find_all('form')`**: 페이지 내의 모든 `<form>` 태그를 찾습니다. `htmli_get.php`에는 1개의 폼이 있습니다.
5.  **`form.get('action')`, `form.get('method')`**: 찾은 폼의 `action` (전송 대상 파일, 이 경우 `htmli_get.php` 자신)과 `method` (`get`) 속성을 추출합니다.
6.  **`form.find_all('input')`**: 폼 태그 내부에서 모든 `<input>` 태그를 찾습니다.
7.  **`[input_tag.get('name') ...]`**: 각 `input` 태그의 `name` 속성 값(bWAPP의 경우 `firstname`, `lastname` 등)을 리스트로 추출합니다. 이 `name` 값들이 바로 다음 단계에서 페이로드를 전송할 때 '키'가 됩니다.

### (4) 이 코드의 한계점과 다음 단계의 필요성
이제 스캔에 필요한 모든 정보를 프로그래밍 방식으로 수집했습니다. 어떤 주소(`action`)로, 어떤 방식(`method`)으로, 어떤 입력 필드(`input_names`)에 데이터를 보내야 하는지 모두 알아냈습니다. 남은 것은 단 하나, 이 정보들을 조합하여 실제로 악성 스크립트 페이로드를 전송하고 서버의 반응을 확인하는 것입니다. 4단계에서 이 모든 것을 자동화하여 스캐너를 완성합니다.

---

## [4단계: 자동화된 XSS 스캐너 완성하기]

### (1) 학습 목표
-   추출한 폼 정보를 바탕으로 XSS 페이로드를 자동으로 구성하고 전송하는 방법을 학습합니다.
-   로그인, 페이지 파싱, 취약점 테스트, 결과 분석의 전 과정을 하나로 합쳐 스캐너의 핵심 로직을 완성합니다.

### (2) 전체 파이썬 코드
```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def run_scanner(session, url):
    """주어진 URL의 폼을 찾아 XSS 스캔을 수행합니다."""
    try:
        print(f"\n[*] Scanning page: {url}")
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        forms = soup.find_all('form')
        if not forms:
            print("  - No forms found on this page.")
            return

        print(f"  - Found {len(forms)} forms.")
        xss_payload = '<script>alert("XSS_VULNERABLE")</script>'

        for form in forms:
            action = form.get('action')
            method = form.get('method', 'get').lower()
            target_url = urljoin(url, action)

            inputs = form.find_all('input')
            data = {}
            for input_tag in inputs:
                input_name = input_tag.get('name')
                input_type = input_tag.get('type', 'text')
                # 텍스트류의 입력 필드에 페이로드 삽입
                if input_name and input_type in ('text', 'search', 'email', 'password'):
                    data[input_name] = xss_payload
                # 다른 타입의 input도 기본값으로 채워줄 수 있음
                elif input_name:
                    data[input_name] = "test"
            
            if not data:
                continue

            print(f"  - Testing form -> {target_url} ({method.upper()})")
            
            try:
                if method == 'post':
                    submission_response = session.post(target_url, data=data)
                else:
                    submission_response = session.get(target_url, params=data)
                
                submission_response.raise_for_status()

                if xss_payload in submission_response.text:
                    print(f"  [!!!] XSS VULNERABILITY FOUND at {target_url}")
                    print(f"      - Payload: {data}")
                else:
                    print("  [-] Form seems secure.")

            except requests.exceptions.RequestException as e:
                print(f"  [!] Failed to submit form: {e}")

    except requests.exceptions.RequestException as e:
        print(f"[!] Error during scan of {url}: {e}")

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    session = requests.Session()
    login_url = "http://127.0.0.1:8888/login.php"
    login_payload = {
        "login": "bee", "password": "bug",
        "security_level": "0", "form": "submit"
    }

    try:
        print("[*] Logging in to bWAPP...")
        login_response = session.post(login_url, data=login_payload)
        login_response.raise_for_status()
        if "Welcome bee" not in login_response.text:
            raise Exception("Login Failed - check credentials or server status.")
        print("[+] Login successful!")

        # 스캔할 페이지 목록
        scan_targets = [
            "http://127.0.0.1:8888/htmli_get.php",
            "http://127.0.0.1:8888/htmli_post.php",
            # 다른 페이지도 추가 가능
        ]

        for target in scan_targets:
            run_scanner(session, target)

    except Exception as e:
        print(f"[!!!] An error occurred: {e}")

```

### (3) 상세한 코드 설명
1.  **`run_scanner(session, url)` 함수**: 스캔 로직을 재사용 가능한 함수로 분리했습니다. 로그인된 `session`과 스캔할 `url`을 인자로 받습니다.
2.  **`xss_payload`**: 식별하기 쉽도록 `alert` 메시지를 `"XSS_VULNERABLE"`로 변경했습니다.
3.  **`data[input_name] = "test"`**: XSS 페이로드를 넣지 않는 다른 입력 필드(hidden, radio 등)도 값을 채워줘야 폼이 정상적으로 제출될 수 있으므로, 기본값 "test"를 넣어줍니다.
4.  **`run_scanner` 호출**: 메인 로직(`if __name__ == "__main__":`)에서 로그인 성공 후, `scan_targets` 리스트에 정의된 각 URL에 대해 `run_scanner` 함수를 호출하여 스캔을 수행합니다.
5.  **결과 분석**: `htmli_get.php`를 스캔하면, `firstname` 또는 `lastname`에 삽입된 XSS 페이로드가 서버 응답에 그대로 포함되어 돌아오므로, `if xss_payload in submission_response.text:` 조건이 참이 되어 "XSS VULNERABILITY FOUND" 메시지가 출력될 것입니다.

---

## 튜토리얼 최종 마무리

축하합니다! 여러분은 이제 로컬 bWAPP 환경에 로그인하고, 페이지를 분석하여, 자동으로 XSS 취약점을 찾아내는 실용적인 웹 스캐너를 완성했습니다. 이론으로만 배우는 것을 넘어, 실제 환경과의 상호작용을 통해 웹 스캐너의 진화 과정을 완벽하게 체험하셨습니다.

### 다음 단계는?

이 스캐너는 강력한 시작점입니다. 이제부터는 여러분의 몫입니다.
-   **크롤러(Crawler) 기능 추가**: 스캔한 페이지에서 새로운 내부 링크(`a` 태그의 `href`)를 수집하고, 그 링크들을 `scan_targets`에 동적으로 추가하여 사이트 전체를 스캔하도록 확장할 수 있습니다.
-   **다양한 취약점 스캔 로직 추가**: SQL Injection(`' OR 1=1--`), 명령어 삽입(`; ls -al`) 등 다른 종류의 취약점 페이로드와 탐지 로직을 `run_scanner` 함수에 추가할 수 있습니다.
-   **결과 리포팅**: 발견된 취약점을 단순히 출력하는 대신, 파일(CSV, JSON)이나 데이터베이스에 체계적으로 저장하는 기능을 추가할 수 있습니다.

여러분은 이제 웹 통신과 자동화된 분석에 대한 깊은 이해를 갖게 되었습니다. 이 지식을 바탕으로 더 안전한 웹을 만드는 데 기여하는 훌륭한 개발자 또는 보안 전문가로 성장하시기를 응원합니다!
