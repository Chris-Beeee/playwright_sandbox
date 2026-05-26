from playwright.sync_api import Page

class GenericMoviesPage:
    def __init__(self, page: Page, url: str):
        self.page = page
        self.url = url
        self.movie_titles = page.locator("h2.whitespace-normal span, h2 a")
        self.accept_cookies_btn = page.locator("button#onetrust-accept-btn-handler")

    def load(self):
        self.page.goto(self.url)

    def accept_cookies(self):
        try:
            if self.accept_cookies_btn.is_visible(timeout=4000):
                self.accept_cookies_btn.click()
        except Exception:
            pass

    def get_movie_titles(self):
        if self.movie_titles.count() > 0:
            self.movie_titles.first.wait_for(state="visible", timeout=10000)
        
        import os
        username = os.getenv("TMDB_USERNAME", "")
        
        titles = self.movie_titles.all_inner_texts()
        return [t.strip() for t in titles if t.strip() and t.strip().lower() != username.lower()]
