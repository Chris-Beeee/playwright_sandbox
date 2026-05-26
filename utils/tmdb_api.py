import os
import requests

MOCK_MOVIES = [
    "The Matrix",
    "Inception",
    "Interstellar",
    "The Dark Knight",
    "Pulp Fiction"
]

def get_now_playing_movies(is_mock=False):
    """
    Fetches the list of 'Now Playing' movies directly from the TMDB API.
    Returns a tuple: (list of movie title strings, boolean indicating if mock data was used).
    """
    if is_mock:
        return MOCK_MOVIES, True
        
    access_token = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
    if not access_token:
        return MOCK_MOVIES, True
        
    url = "https://api.themoviedb.org/3/movie/now_playing"
    # Added region="GB" to match your local IP address where Selenium is running
    params = {"language": "en-US", "page": 1, "region": "GB"}
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    return [movie['title'] for movie in data.get("results", [])], False


def get_movies_from_api(endpoint, is_mock=False):
    """
    Fetches the list of movies directly from the TMDB API for a specific endpoint.
    Endpoints: 'now_playing', 'popular', 'upcoming', 'top_rated'
    Returns a tuple: (list of movie title strings, boolean indicating if mock data was used).
    """
    if is_mock:
        return MOCK_MOVIES, True
        
    access_token = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
    if not access_token:
        return MOCK_MOVIES, True
        
    url = f"https://api.themoviedb.org/3/movie/{endpoint}"
    # Added region="GB" to match your local IP address where Selenium is running
    params = {"language": "en-US", "page": 1, "region": "GB"}
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    return [movie['title'] for movie in data.get("results", [])], False

def get_discovered_movies(filters: dict, is_mock=False):
    """
    Fetches the list of movies from the TMDB /discover/movie endpoint using given filters.
    Returns a tuple: (list of movie title strings, boolean indicating if mock data was used).
    """
    if is_mock:
        return MOCK_MOVIES, True
        
    access_token = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
    if not access_token:
        return MOCK_MOVIES, True
        
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {"language": "en-US", "page": 1, "region": "GB"}
    params.update(filters) # merge in the dynamic filters
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    return [movie['title'] for movie in data.get("results", [])], False

_GENRE_CACHE = {}

def get_genre_id(genre_name: str) -> str:
    """
    Fetches the TMDB movie genre list and returns the ID for the given genre name.
    Caches the genres to a local file to avoid repeated API calls.
    """
    import json
    global _GENRE_CACHE
    
    # Load from cache memory if already loaded
    if _GENRE_CACHE:
        return str(_GENRE_CACHE.get(genre_name.lower()))
        
    cache_file = os.path.join(os.path.dirname(__file__), "genres.json")
    
    # Load from file if exists
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            _GENRE_CACHE = json.load(f)
            if genre_name.lower() in _GENRE_CACHE:
                return str(_GENRE_CACHE[genre_name.lower()])
                
    # Otherwise, fetch from API
    access_token = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
    if not access_token:
        # Fallback hardcoded list if we don't have token but need one
        _GENRE_CACHE = {"action": 28, "romance": 10749}
        return str(_GENRE_CACHE.get(genre_name.lower()))
        
    url = "https://api.themoviedb.org/3/genre/movie/list"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    genres = response.json().get("genres", [])
    
    # Rebuild cache
    _GENRE_CACHE = {g["name"].lower(): g["id"] for g in genres}
    
    # Save to local file
    with open(cache_file, "w") as f:
        json.dump(_GENRE_CACHE, f, indent=4)
        
    return str(_GENRE_CACHE.get(genre_name.lower()))

_KEYWORD_CACHE = {}

def get_keyword_id(keyword_name: str) -> str:
    """
    Searches the TMDB API for a specific keyword and returns its ID.
    Since there are too many keywords to download at once, it dynamically caches 
    individual keywords as they are queried to a local file.
    """
    import json
    global _KEYWORD_CACHE
    
    keyword_lower = keyword_name.lower()
    
    # Load from memory if present
    if keyword_lower in _KEYWORD_CACHE:
        return str(_KEYWORD_CACHE[keyword_lower])
        
    cache_file = os.path.join(os.path.dirname(__file__), "keywords.json")
    
    # Load from file if exists
    if os.path.exists(cache_file) and not _KEYWORD_CACHE:
        with open(cache_file, "r") as f:
            _KEYWORD_CACHE = json.load(f)
            
    if keyword_lower in _KEYWORD_CACHE:
        return str(_KEYWORD_CACHE[keyword_lower])
        
    # Fetch from API
    access_token = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
    if not access_token:
        # Fallback if no token
        _KEYWORD_CACHE = {"alien": 9951}
        return str(_KEYWORD_CACHE.get(keyword_lower, ""))
        
    url = "https://api.themoviedb.org/3/search/keyword"
    params = {"query": keyword_name, "page": 1}
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    results = response.json().get("results", [])
    
    # Try to find exact match, otherwise take the first one
    keyword_id = None
    for res in results:
        if res["name"].lower() == keyword_lower:
            keyword_id = res["id"]
            break
            
    if not keyword_id and results:
        keyword_id = results[0]["id"]
        
    if keyword_id:
        _KEYWORD_CACHE[keyword_lower] = keyword_id
        with open(cache_file, "w") as f:
            json.dump(_KEYWORD_CACHE, f, indent=4)
        return str(keyword_id)
        
    return ""

def build_api_filters(scenario: dict) -> dict:
    """
    Translates user-friendly scenario filter choices into TMDB API /discover/movie parameters.
    """
    api_params = {}
    
    # 1. Genre
    genre = scenario.get("genre")
    if genre:
        genre_id = get_genre_id(genre)
        if genre_id:
            api_params["with_genres"] = genre_id
            
    # 2. Keyword
    keyword = scenario.get("keyword")
    if keyword:
        keyword_id = get_keyword_id(keyword)
        if keyword_id:
            api_params["with_keywords"] = keyword_id
            
    # 3. Release Dates
    if scenario.get("start_date"):
        api_params["release_date.gte"] = scenario["start_date"]
    if scenario.get("end_date"):
        api_params["release_date.lte"] = scenario["end_date"]
        
    # 4. Certifications (e.g. ["PG", "15"])
    certs = scenario.get("certifications")
    if certs:
        api_params["certification"] = "|".join(certs)
        api_params["certification_country"] = "GB"  # Default to UK region for consistency
        
    # 5. User Score (Vote Average)
    if scenario.get("min_score") is not None:
        api_params["vote_average.gte"] = scenario["min_score"]
    if scenario.get("max_score") is not None:
        api_params["vote_average.lte"] = scenario["max_score"]
        
    # 6. Minimum User Votes
    if scenario.get("min_votes") is not None:
        api_params["vote_count.gte"] = scenario["min_votes"]
        
    # 7. Original Language
    if scenario.get("language"):
        api_params["with_original_language"] = scenario["language"]
        
    # 8. Runtime
    if scenario.get("min_runtime") is not None:
        api_params["with_runtime.gte"] = scenario["min_runtime"]
    if scenario.get("max_runtime") is not None:
        api_params["with_runtime.lte"] = scenario["max_runtime"]
        
    # 9. Availabilities (Monetization Types)
    availabilities = scenario.get("availabilities")
    if availabilities:
        api_params["with_watch_monetization_types"] = "|".join(availabilities)
        api_params["watch_region"] = "GB"  # Match UK watch region
        
    return api_params

