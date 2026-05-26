from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.login_link = page.locator("a[href='/login']").first
        self.username_input = page.locator("input#username")
        self.password_input = page.locator("input#password")
        self.submit_button = page.locator("input#login_button")
        self.profile_link = page.locator("a[href^='/u/']").first

    def navigate(self):
        """Navigate to the TMDB home page."""
        self.page.goto("https://www.themoviedb.org/")

    def click_login_link(self):
        """Click the login link in the top navigation."""
        self.login_link.click()

    def login(self, username, password):
        """Fill in credentials and submit the login form."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()
