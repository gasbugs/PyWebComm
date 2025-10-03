# 나만의 웹 스캐너 만들기 (PyWebComm)

이 프로젝트는 파이썬을 사용하여 기초적인 웹 취약점 스캐너를 단계별로 만들어보는 튜토리얼 실습 저장소입니다. 원시적인 소켓 통신부터 시작하여, `requests`와 `BeautifulSoup` 같은 현대적인 라이브러리를 활용하고, 최종적으로는 Docker를 통해 어디서든 실행 가능한 커맨드 라인 도구를 완성하는 과정을 담고 있습니다.

## ✨ 주요 기능

- **폼(Form) 기반 XSS 스캔**: 웹 페이지의 폼을 자동으로 탐색하고, XSS 페이로드를 삽입하여 취약점을 탐지합니다.
- **설정 가능한 보안 레벨**: bWAPP과 같은 테스트 환경의 보안 레벨(low, high)에 맞춰 스캔을 수행합니다.
- **모듈화된 구조**: 각 기능(로그인, 파싱, 스캔)이 단계별 모듈로 분리되어 학습 및 확장이 용이합니다.
- **Docker 지원**: Docker를 통해 파이썬이나 라이브러리가 설치되지 않은 환경에서도 일관되게 스캐너를 실행할 수 있습니다.

## 📂 프로젝트 구조

프로젝트는 튜토리얼의 각 단계를 나타내는 디렉토리로 구성되어 있습니다.

```
PyWebComm/
├── step1_socket_basic/         # 1단계: 원시 소켓 통신
├── step2_requests_login/       # 2단계: requests를 이용한 로그인
├── step3_parser_and_extract/   # 3단계: BeautifulSoup을 이용한 파싱
├── step4_final_scanner/        # 4단계: 최종 스캐너 (메인 스크립트)
├── step5_security_level_test/  # 5단계: 보안 레벨 변경 테스트
├── requirements.txt            # 파이썬 의존성 목록
├── Dockerfile                  # Docker 이미지 빌드 파일
└── README.md                   # 프로젝트 안내 문서
```

## 🚀 시작하기

이 스캐너를 실행하기 위한 방법은 두 가지가 있습니다: 로컬 파이썬 환경 또는 Docker.

### 1. 로컬 파이썬 환경에서 실행

**사전 준비:**
- Python 3.8 이상
- 스캔 대상 웹 애플리케이션 (예: `http://127.0.0.1:8888`에서 실행 중인 bWAPP)

**설치 및 실행:**

1.  **의존성 설치**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **스캐너 실행**:
    `step4_final_scanner/scanner.py`가 메인 스크립트입니다. `--level` 옵션으로 보안 레벨을 지정할 수 있습니다.

    *   **낮은 보안 레벨로 스캔 (취약점 발견 예상):**
        ```bash
        python step4_final_scanner/scanner.py --level 0
        ```

    *   **높은 보안 레벨로 스캔 (방어 확인):**
        ```bash
        python step4_final_scanner/scanner.py --level 2
        ```

### 2. Docker를 사용하여 실행

**사전 준비:**
- Docker
- 스캔 대상 웹 애플리케이션 (로컬에서 실행 중이어야 함)

**빌드 및 실행:**

1.  **Docker 이미지 빌드**:
    프로젝트 루트 디렉토리에서 아래 명령어를 실행하여 `my-web-scanner`라는 이름의 이미지를 빌드합니다.
    ```bash
    docker build -t my-web-scanner .
    ```

2.  **Docker 컨테이너 실행**:
    `--network="host"` 옵션은 컨테이너가 로컬호스트(127.0.0.1)의 bWAPP 서버에 접속하기 위해 필요합니다.

    *   **스캐너 도움말 확인:**
        ```bash
        docker run --rm --network="host" my-web-scanner
        ```

    *   **낮은 보안 레벨로 스캔 실행:**
        ```bash
        docker run --rm --network="host" my-web-scanner python step4_final_scanner/scanner.py --level 0
        ```

## ✅ 테스트 실행하기

프로젝트에는 각 단계의 기능이 올바르게 동작하는지 검증하는 테스트 코드가 포함되어 있습니다. `pytest`를 사용하여 실행할 수 있습니다.

-   **모든 테스트 실행:**
    ```bash
    pytest
    ```

-   **특정 단계의 테스트만 실행:**
    ```bash
    # 4단계 스캐너의 취약점 탐지 기능 테스트
    pytest step4_final_scanner/test_scanner.py

    # 5단계 높은 보안 레벨에서의 방어 기능 테스트
    pytest step5_security_level_test/test_step5.py
    ```
