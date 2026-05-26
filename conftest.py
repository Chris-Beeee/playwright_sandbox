import pytest
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

AUTH_FILE = Path(".auth/state.json")

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption("--mock-api", action="store_true", help="Run tests against mock API")

@pytest.fixture(scope="session", autouse=True)
def setup_auth(request):
    """
    Session-scoped fixture to perform login once and save the state.
    """
    is_mock_mode = request.config.getoption("--mock-api", default=False)
        
    username = os.getenv("TMDB_USERNAME")
    password = os.getenv("TMDB_PASSWORD")

    # Only log in if we aren't in mock mode and have credentials
    if not is_mock_mode and username and password:
        # Create .auth directory if it doesn't exist
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # We login if the file doesn't exist, to save time on repeat runs
        if not AUTH_FILE.exists():
            print("\n[Auth] Performing global login and saving state...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False) # Headless=False to bypass TMDB bot block
                context = browser.new_context()
                page = context.new_page()
                
                # Navigate and login
                page.goto("https://www.themoviedb.org/")
                page.locator("a[href='/login']").first.click()
                page.locator("input#username").fill(username)
                page.locator("input#password").fill(password)
                page.locator("input#login_button").click()
                
                # Wait for successful login
                page.wait_for_selector("a[href^='/u/']", timeout=10000)
                
                # Save storage state
                context.storage_state(path=AUTH_FILE)
                browser.close()

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Inject the saved authentication state into all tests.
    """
    if AUTH_FILE.exists():
        return {
            **browser_context_args,
            "storage_state": str(AUTH_FILE),
        }
    return browser_context_args
