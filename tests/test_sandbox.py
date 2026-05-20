import re
import pytest
from playwright.sync_api import expect

def test_google_search_sandbox(page):
    """
    A simple sandbox test that navigates to Google, performs a search, 
    and verifies that the results page loaded successfully.
    """
    # 1. Navigate to google.com
    page.goto("https://www.google.com")

    # 2. Handle Google's cookie consent dialog if it appears
    # (Checking if the consent button exists and is visible before clicking)
    accept_button = page.get_by_role("button", name="Accept all")
    if accept_button.is_visible():
        accept_button.click()

    # 3. Locate the search input field, fill in a query, and press Enter
    # Google's search input uses the title "Search" or name "q"
    search_input = page.locator("textarea[name='q']")
    search_input.fill("Playwright Python")
    search_input.press("Enter")

    # 4. Assert that the search result container or specific elements are visible
    # Verify that the page URL now contains the search query
    expect(page).to_have_url(re.compile(r".*search.*"))
