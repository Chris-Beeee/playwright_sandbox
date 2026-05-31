# Playwright Pytest

A lightweight, pre-configured sandbox template for writing and running end-to-end (E2E) web automation tests using **Python**, **pytest**, and **Playwright**.

---

## Quick Start (Onboarding)

We have provided a bootstrap script that automates the creation of the virtual environment, updates `pip`, installs the requirements, and downloads the required Playwright browser engines.

### Setup (Windows)
Double-click the `setup.bat` file in the root directory, or run it via your terminal:
```cmd
.\setup.bat
```

*Note: For macOS/Linux users, you can manually run:*
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

---

## Environment Variables & Credentials

Create a `.env` file in the root directory to provide your TMDB credentials and API read access token.

- `TMDB_USERNAME` and `TMDB_PASSWORD` are used for front-end user login testing.
- `TMDB_API_READ_ACCESS_TOKEN` is used by the test suite to query the TMDB API and verify that the UI results accurately match the backend database.

**Note on Missing Credentials (Fallback Behavior)**:
- If `TMDB_USERNAME` and `TMDB_PASSWORD` are omitted, the global login setup is skipped, and the tests will execute seamlessly as an anonymous guest user.
- If `TMDB_API_READ_ACCESS_TOKEN` is omitted, the tests will automatically fallback to "Mock API" mode. The API queries will not execute, and the scraped UI results will be evaluated against a static list of mock titles instead.

```env
TMDB_USERNAME=your_username
TMDB_PASSWORD=your_password
TMDB_API_READ_ACCESS_TOKEN=your_api_read_access_token
```

---

## Running Tests

Once the setup is complete, activate your virtual environment:
```cmd
# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

You can now run your test suite with `pytest`:

| Mode | Command | Description |
| :--- | :--- | :--- |
| **Headless (Default)** | `pytest` | Runs tests fast and silently in the background. |
| **Headed** | `pytest --headed` | Launches a visible browser window so you can watch execution. |
| **Slow Motion** | `pytest --headed --slowmo 1000` | Introduces a 1-second delay between browser steps (great for debugging). |

---

## Advanced Debugging & Tracing

One of Playwright's most powerful features is **Tracing**, which records DOM changes, console logs, network requests, and screenshots of every single action during a test run.

### Recording a Trace on Failure
To record a trace zip-file only when a test fails:
```bash
pytest --tracing retain-on-failure
```

If a test fails, a `test-results/` directory will be created containing a `.zip` file. 

### Viewing a Trace
Upload the generated trace `.zip` file to [trace.playwright.dev](https://trace.playwright.dev) in your browser to inspect execution frame-by-frame.

---

## Project Structure

```text
Playwright_sandbox/
├── .venv/               # Virtual environment directory (automatically created)
├── tests/               # Your test files
│   └── test_sandbox.py  # Standard Google Search template test
├── pytest.ini           # Configuration settings for pytest discovery
├── requirements.txt     # Python package dependencies
└── setup.bat            # Automated onboarding script for Windows
```
