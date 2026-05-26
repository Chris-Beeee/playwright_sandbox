import pytest
from selenium import webdriver
from dotenv import load_dotenv

import os
from pages.tmdb_pages import TMDBGenericMoviesPage, TMDBHomePage, TMDBLoginPage
from utils.tmdb_api import get_movies_from_api
from utils.backend_verifier import verify_scraped_against_backend

load_dotenv()

@pytest.mark.parametrize("category, ui_url, api_endpoint", [
    ("Now Playing", "https://www.themoviedb.org/movie/now-playing", "now_playing"),
    ("Popular",     "https://www.themoviedb.org/movie",             "popular"),
    ("Upcoming",    "https://www.themoviedb.org/movie/upcoming",    "upcoming"),
    ("Top Rated",   "https://www.themoviedb.org/movie/top-rated",   "top_rated")
])
def test_tmdb_movies_categories_verification(category, ui_url, api_endpoint, record_property, is_mock_mode):
    # 1. Fetch backend expected data via API
    try:
        backend_titles, is_mock = get_movies_from_api(api_endpoint, is_mock=is_mock_mode)
        mode_str = "MOCK" if is_mock else "API"
        api_msg = f"[{mode_str}] Successfully retrieved {len(backend_titles)} '{category}' movies from the backend."
        print(f"\n{api_msg}")
        record_property("api_msg", api_msg)
    except Exception as e:
        pytest.fail(f"TEST FAILED: Could not fetch from API. Error: {str(e)}", pytrace=False)

    # 2. Scrape the UI via Selenium POM
    scraped_titles = []
    ui_error = None
    
    try:
        driver = webdriver.Chrome()
        try:
            driver.maximize_window()
            
            # Conditionally log in to ensure region-specific API matching is accurate
            if not is_mock_mode and os.getenv("TMDB_USERNAME") and os.getenv("TMDB_PASSWORD"):
                home_page = TMDBHomePage(driver)
                home_page.load()
                home_page.click_login()
                
                login_page = TMDBLoginPage(driver)
                login_page.login(os.getenv("TMDB_USERNAME"), os.getenv("TMDB_PASSWORD"))
                if not login_page.is_login_successful():
                    pytest.fail("Failed to login during UI setup for categories test.")

            # We use the generic page object which accepts any category URL
            movies_page = TMDBGenericMoviesPage(driver, ui_url)
            movies_page.load()
            movies_page.accept_cookies()
            
            scraped_titles = movies_page.get_movie_titles()
            ui_msg = f"[UI] Successfully scraped {len(scraped_titles)} '{category}' movie titles from the web page."
            print(ui_msg)
            record_property("ui_msg", ui_msg)
        finally:
            driver.quit()
    except Exception as e:
        from selenium.common.exceptions import TimeoutException
        if isinstance(e, TimeoutException):
            ui_error = "TimeoutException: Selenium timed out. The movie titles never appeared on screen, or the page took too long to load."
        else:
            error_msg = str(e).split('Stacktrace:')[0].strip()
            ui_error = f"{type(e).__name__}: {error_msg}"
        
    if ui_error:
        pytest.fail(f"TEST FAILED: Selenium encountered an error during UI setup or scraping. Details: {ui_error}", pytrace=False)

    if not scraped_titles:
        pytest.fail(f"TEST FAILED: Could not scrape any '{category}' movie titles from the UI.", pytrace=False)

    # 3. Verify that the UI titles match the Backend titles
    try:
        match_count = verify_scraped_against_backend(scraped_titles, backend_titles, is_mock=is_mock, threshold=0.6)
        match_msg = f"[VERIFIER] Successfully matched {match_count} movies between UI and API."
        print(match_msg)
        record_property("match_msg", match_msg)
    except AssertionError as e:
        pytest.fail(str(e), pytrace=False)
