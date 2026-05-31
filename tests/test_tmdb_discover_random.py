import pytest
import os
import random
from dotenv import load_dotenv
import json

from pages.discover_page import DiscoverPage
from utils.tmdb_api import build_api_filters, get_discovered_movies
from utils.backend_verifier import verify_scraped_against_backend

load_dotenv()

def load_genres():
    try:
        # Load available genres from our util file
        with open("utils/genres.json", "r") as f:
            data = json.load(f)
            # The genre keys in the JSON are lowercase, but UI needs Title Case
            return [k.title() for k in data.keys()]
    except Exception:
        return ["Action", "Comedy", "Drama", "Horror", "Romance"]

def generate_random_scenarios(num_scenarios=5):
    scenarios = []
    genres = load_genres()
    languages = ["en", "fr", "es", "de", "it", "ja"]
    availabilities_options = [
        ["flatrate"], ["rent"], ["buy"], ["flatrate", "rent"], None
    ]
    
    for i in range(num_scenarios):
        min_score = random.randint(0, 7)
        max_score = random.randint(min_score + 1, 10)
        min_runtime = random.randint(30, 90)
        max_runtime = random.randint(100, 200)
        
        scenario = {
            "name": f"Random_Scenario_{i+1}",
            "genre": random.choice(genres + [None]),
            "keyword": None, # Kept None to avoid 0 results randomly due to niche keywords
            "start_date": None,
            "end_date": None,
            "certifications": None,
            "min_score": min_score,
            "max_score": max_score,
            "min_votes": random.randint(0, 50),
            "language": random.choice(languages + [None]),
            "min_runtime": min_runtime,
            "max_runtime": max_runtime,
            "availabilities": random.choice(availabilities_options),
            "show_me": "Everything"
        }
        scenarios.append(scenario)
    return scenarios

# You can modify the number of random scenarios here
NUM_SCENARIOS = 5
RANDOM_SCENARIOS = generate_random_scenarios(NUM_SCENARIOS)

@pytest.mark.parametrize("scenario", RANDOM_SCENARIOS)
def test_tmdb_discover_filters_random(page, request, record_property, scenario):
    is_mock_mode = False
    if hasattr(request.config.option, "mock_api"):
        is_mock_mode = request.config.getoption("--mock-api")

    print(f"\n--- Running Random Scenario: {scenario['name']} ---")
    print(f"Parameters: {scenario}")
    
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
    discover_page = DiscoverPage(page)
    discover_page.load()
    discover_page.accept_cookies()
    
    # Apply filters dynamically if provided in the scenario dictionary
    if scenario.get("show_me"):
        discover_page.select_show_me(scenario["show_me"])
        
    if scenario.get("genre"):
        discover_page.select_genre(scenario["genre"])
        
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

    # 3. Verify that the UI titles match the Backend titles
    try:
        match_count = verify_scraped_against_backend(scraped_titles, backend_titles, is_mock=is_mock, threshold=0.85)
        match_msg = f"[VERIFIER] Successfully matched {match_count} movies between UI and API."
        print(match_msg)
        record_property("match_msg", match_msg)
    except Exception as e:
        pytest.fail(f"TEST FAILED: Verification logic encountered an error. Error: {e}", pytrace=False)

    if len(backend_titles) > 0 and match_count == 0 and not is_mock_mode:
        pytest.fail("TEST FAILED: Zero matching movies found between the UI and the Backend API.", pytrace=False)
