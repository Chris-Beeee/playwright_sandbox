import os
import time
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Load the environment variables from the .env file
load_dotenv()

def test_tmdb_login(is_mock_mode):
    if is_mock_mode:
        pytest.skip("Skipping login tests because --mock-api flag is active.")
    # Load credentials from environment
    username = os.getenv("TMDB_USERNAME")
    password = os.getenv("TMDB_PASSWORD")
    
    if not username or not password:
        pytest.fail("TMDB_USERNAME or TMDB_PASSWORD not found in environment variables.")

    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        # 1. Navigate to TMDB
        driver.get("https://www.themoviedb.org/")
        
        # 2. Click login button on the top nav
        login_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/login']"))
        )
        login_link.click()
        
        # 3. Wait for login page to load and find input fields
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#username"))
        )
        password_field = driver.find_element(By.CSS_SELECTOR, "input#password")
        
        # TMDB's login button is typically an input or button with id login_button
        submit_button = driver.find_element(By.CSS_SELECTOR, "input#login_button")
        
        # 4. Enter credentials
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # 5. Click login
        submit_button.click()
        
        # 6. Verify successful login
        # After login, you are usually redirected to your profile or the home page,
        # and a user avatar or profile link becomes visible.
        login_success = False
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/u/']"))
            )
            login_success = True
            print("\nLogin successful!")
        except TimeoutException:
            pass
            
        if not login_success:
            pytest.fail("TEST FAILED: Incorrect credentials or login took too long.", pytrace=False)
        
    finally:
        driver.quit()
