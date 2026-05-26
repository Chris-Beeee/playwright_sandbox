import pytest
import os
from dotenv import load_dotenv

from pages.discover_page import DiscoverPage
from pages.login_page import LoginPage
from utils.tmdb_api import get_discovered_movies, get_genre_id, get_keyword_id
from utils.backend_verifier import verify_scraped_against_backend

load_dotenv()

@pytest.mark.parametrize("scenario", [
    {
        "name": "Action_Alien_2020_to_2023",
        "genre": "Action",
        "keyword": "alien",
        "start_date": "2020-01-01",
        "end_date": "2023-12-31"
    },
    {
        "name": "Romance_Love_No_Dates",
        "genre": "Romance",
        "keyword": "love",
        "start_date": None,
        "end_date": None
    }
])
def test_tmdb_discover_filters(page, request, record_property, scenario):
    is_mock_mode = False
    if hasattr(request.config.option, "mock_api"):
        is_mock_mode = request.config.getoption("--mock-api")

    print(f"\n--- Running Scenario: {scenario['name']} ---")
    
    # 1. Prepare expected API parameters
    api_filters = {
        "with_genres": get_genre_id(scenario["genre"]),
        "with_keywords": get_keyword_id(scenario["keyword"])
    }
    
    if scenario["start_date"]:
        api_filters["release_date.gte"] = scenario["start_date"]
    if scenario["end_date"]:
        api_filters["release_date.lte"] = scenario["end_date"]

    try:
        backend_titles, is_mock = get_discovered_movies(api_filters, is_mock=is_mock_mode)
        api_msg = f"[API] Successfully retrieved {len(backend_titles)} discovered movies from the backend."
        print(api_msg)
        record_property("api_msg", api_msg)
    except Exception as e:
        pytest.fail(f"TEST FAILED: Could not fetch expected data from API Backend. Error: {e}", pytrace=False)

    # 2. Scrape the UI
    # Note: Login is now handled globally via conftest.py and injected via storage_state

    discover_page = DiscoverPage(page)
    discover_page.load()
    discover_page.accept_cookies()
    
    discover_page.select_show_me("Everything")
    discover_page.select_genre(scenario["genre"])
    discover_page.add_keyword(scenario["keyword"])
    
    if scenario["start_date"] and scenario["end_date"]:
        discover_page.set_release_dates(scenario["start_date"], scenario["end_date"])
    
    discover_page.apply_filters()
    
    scraped_titles = discover_page.get_movie_titles()
    ui_msg = f"[UI] Successfully scraped {len(scraped_titles)} movie titles after filtering."
    print(ui_msg)
    record_property("ui_msg", ui_msg)

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
