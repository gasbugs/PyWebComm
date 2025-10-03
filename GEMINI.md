# Gemini Context: PyWebComm Project

## Project Overview

This project, PyWebComm, is a hands-on Python tutorial for building a web vulnerability scanner from scratch. The primary documentation and code are located in `prd.md`.

The tutorial is designed for beginners and demonstrates the evolution of a web client, starting from low-level socket programming to using high-level libraries for sophisticated interactions. The end goal is to produce a functional scanner capable of logging into a web application and testing for reflected Cross-Site Scripting (XSS) vulnerabilities.

**Key Technologies:**
- **Language:** Python
- **Libraries:** `socket`, `requests`, `beautifulsoup4`

**Target Environment:**
The scanner is specifically designed to run against a local instance of the bWAPP (buggy web application), expected to be running at `http://127.0.0.1:8888`.

## Building and Running

Currently, the project exists as a set of code snippets within the `prd.md` tutorial file. There are no standalone executable scripts yet.

**To run the code:**

1.  **Prerequisites:**
    *   A running instance of the bWAPP environment at `http://127.0.0.1:8888`.
    *   Python 3 installed.

2.  **Install Dependencies:**
    The project requires the `requests` and `beautifulsoup4` libraries. Install them using pip:
    ```bash
    pip install requests beautifulsoup4
    ```

3.  **Execution:**
    Copy the Python code blocks from each step in `prd.md` into a Python file (e.g., `scanner.py`) and execute it:
    ```bash
    python scanner.py
    ```

**TODO:**
- Create a `requirements.txt` file to formalize dependencies.
- Consolidate the final code from the tutorial into a main `scanner.py` script.

## Development Conventions

- The code is structured in a procedural style, organized into functions (e.g., `run_scanner`).
- The project follows a multi-stage tutorial format, with each stage building upon the previous one.
- The code includes comments to explain key logic steps.
- The primary focus is on educational clarity, demonstrating concepts like session management, form submission, and response analysis for vulnerability detection.
