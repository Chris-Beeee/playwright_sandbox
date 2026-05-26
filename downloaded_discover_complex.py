import pytest
import os
from selenium import webdriver
from dotenv import load_dotenv

from pages.tmdb_pages import TMDBDiscoverPage, TMDBHomePage, TMDBLoginPage
from utils.tmdb_api import build_api_filters, get_discovered_movies
from utils.backend_verifier import verify_scraped_against_backend

load_dotenv()

@pytest.mark.parametrize("scenario", [
    {
        "name": "Complex_Comedy_French_Holiday",
        "genre": "Comedy",
        "keyword": "holiday",
        "start_date": None,
        "end_date": None,
        "certifications": ["12", "15"],
        "min_score": 5.0,
        "max_score": 10.0,
        "min_votes": 50,
        "language": "fr",  # French
        "min_runtime": 80,
        "max_runtime": 180,
        "availabilities": ["flatrate", "rent"],
        "show_me": "Everything"
    },
    {
        "name": "Partial_Action_English_No_Keyword",
        "genre": "Action",
        "keyword": None,
        "start_date": None,
        "end_date": None,
        "certifications": None,
        "min_score": 6.0,
        "max_score": 10.0,
        "min_votes": 100,
        "language": "en",  # English
        "min_runtime": 90,
        "max_runtime": 160,
        "availabilities": None,
        "show_me": "Everything"
    }
])
def test_tmdb_discover_filters_complex(is_mock_mode, record_property, scenario):
    print(f"\n--- Running Complex Scenario: {scenario['name']} ---")
    
    # 1. Prepare expected API parameters using our advanced mapping helper
    api_filters = build_api_filters(scenario)
    
    try:
        backend_titles, is_mock = get_discovered_movies(api_filters, is_mock=is_mock_mode)
        api_msg = f"[API] Successfully retrieved {len(backend_titles)} discovered movies from the backend."
        print(api_msg)
        record_property("api_msg", api_msg)
    except Exception as e:
        pytest.fail(f"TEST FAILED: Could not fetch expected data from API Backend. Error: {e}", pytrace=False)

    # 2. Scrape the UI
    scraped_titles = []
    
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    # Conditionally log in if credentials exist and we're not in mock mode
    if not is_mock_mode and os.getenv("TMDB_USERNAME") and os.getenv("TMDB_PASSWORD"):
        home_page = TMDBHomePage(driver)
        home_page.load()
        home_page.click_login()
        
        login_page = TMDBLoginPage(driver)
        login_page.login(os.getenv("TMDB_USERNAME"), os.getenv("TMDB_PASSWORD"))
        if not login_page.is_login_successful():
            pytest.fail("Failed to login during UI setup for discover test.")

    discover_page = TMDBDiscoverPage(driver)
    discover_page.load()
    discover_page.accept_cookies()
    
    # Apply filters dynamically if provided in the scenario dictionary
    if scenario.get("show_me"):
        discover_page.select_show_me(scenario["show_me"])
        
    if scenario.get("genre"):
        discover_page.select_genre(scenario["genre"])
        
    if scenario.get("keyword"):
        discover_page.add_keyword(scenario["keyword"])
        
    if scenario.get("start_date") and scenario.get("end_date"):
        discover_page.set_release_dates(scenario["start_date"], scenario["end_date"])
        
    if scenario.get("certifications"):
        discover_page.set_certifications(scenario["certifications"])
        
    if scenario.get("min_score") is not None and scenario.get("max_score") is not None:
        discover_page.set_user_score_range(scenario["min_score"], scenario["max_score"])
        
    if scenario.get("min_votes") is not None:
        discover_page.set_minimum_user_votes(scenario["min_votes"])
        
    if scenario.get("language"):
        discover_page.select_language(scenario["language"])
        
    if scenario.get("min_runtime") is not None and scenario.get("max_runtime") is not None:
        discover_page.set_runtime_range(scenario["min_runtime"], scenario["max_runtime"])
        
    if scenario.get("availabilities") is not None:
        discover_page.set_availabilities(scenario["availabilities"])
    
    discover_page.apply_filters()
    
    scraped_titles = discover_page.get_movie_titles()
    ui_msg = f"[UI] Successfully scraped {len(scraped_titles)} movie titles after filtering."
    print(ui_msg)
    record_property("ui_msg", ui_msg)
    driver.quit()

    if not scraped_titles:
        pytest.fail("TEST FAILED: Could not scrape any movie titles from the UI after applying filters.", pytrace=False)

    # 3. Verify that the UI titles match the Backend titles
    try:
        match_count = verify_scraped_against_backend(scraped_titles, backend_titles, is_mock=is_mock, threshold=0.85)
        match_msg = f"[VERIFIER] Successfully matched {match_count} movies between UI and API."
        print(match_msg)
        record_property("match_msg", match_msg)
    except Exception as e:
        pytest.fail(f"TEST FAILED: Verification logic encountered an error. Error: {e}", pytrace=False)

    if match_count == 0 and not is_mock_mode:
        pytest.fail("TEST FAILED: Zero matching movies found between the UI and the Backend API.", pytrace=False)
