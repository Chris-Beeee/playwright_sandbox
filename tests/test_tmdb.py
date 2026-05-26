import os
import pytest
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
from pages.login_page import LoginPage

# Load the environment variables from the .env file
load_dotenv()

def test_tmdb_login(page: Page, request: pytest.FixtureRequest):
    # Support for a custom --mock-api flag if configured in conftest.py
    is_mock_mode = False
    if hasattr(request.config.option, "mock_api"):
        is_mock_mode = request.config.getoption("--mock-api")
        
    if is_mock_mode:
        pytest.skip("Skipping login tests because --mock-api flag is active.")
        
    # Load credentials from environment
    username = os.getenv("TMDB_USERNAME")
    password = os.getenv("TMDB_PASSWORD")
    
    if not username or not password:
        pytest.fail("TMDB_USERNAME or TMDB_PASSWORD not found in environment variables.")

    login_page = LoginPage(page)

    # 1. Navigate to TMDB (will use saved auth state)
    login_page.navigate()
    
    # 2. Verify successful login
    try:
        expect(login_page.profile_link).to_be_visible(timeout=10000)
        print("\nLogin successful!")
    except AssertionError:
        pytest.fail("TEST FAILED: Incorrect credentials or login took too long.", pytrace=False)
