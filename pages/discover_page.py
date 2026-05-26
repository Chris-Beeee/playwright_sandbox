from playwright.sync_api import Page, expect

class DiscoverPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "https://www.themoviedb.org/movie"
        self.search_button = page.locator("div.apply.small.background_color.light_blue a")
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

    def select_show_me(self, option_text):
        self.page.locator(f"//label[contains(text(), '{option_text}')]").click()

    def select_genre(self, genre_name):
        self.page.locator(f"//ul[@id='with_genres']/li/a[text()='{genre_name}']").click()

    def add_keyword(self, keyword):
        self.page.locator("span.k-multiselect input.k-input-inner").fill(keyword)
        self.page.wait_for_timeout(1500) # wait for dropdown
        self.page.locator(f"//ul[@id='with_keywords_listbox']/li[translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{keyword.lower()}']").click()

    def set_release_dates(self, start_date, end_date):
        start_input = self.page.locator("input#release_date_gte")
        start_input.fill(start_date)
        start_input.press("Tab")
        
        end_input = self.page.locator("input#release_date_lte")
        end_input.fill(end_date)
        end_input.press("Tab")

    def set_certifications(self, certs):
        if not certs:
            return
        for cert in certs:
            loc = self.page.locator(f"//ul[@id='certification']/li[@data-value='{cert}']")
            classes = loc.get_attribute("class") or ""
            if "selected" not in classes:
                loc.click()

    def set_user_score_range(self, min_score, max_score):
        self.page.evaluate(
            '''([min, max]) => {
                var slider = $("#user_score_range").data("kendoRangeSlider");
                if (slider) {
                    slider.values(min, max);
                    slider.trigger("change");
                } else {
                    $("#vote_average_gte").val(min);
                    $("#vote_average_lte").val(max);
                }
            }''', [min_score, max_score]
        )

    def set_minimum_user_votes(self, min_votes):
        self.page.evaluate(
            '''(min_v) => {
                var slider = $("#user_vote_range").data("kendoSlider");
                if (slider) {
                    slider.value(min_v);
                    slider.trigger("change");
                } else {
                    $("#user_vote_range").val(min_v);
                }
            }''', min_votes
        )

    def select_language(self, lang_code):
        self.page.evaluate(
            '''(lang) => {
                var ddl = $("#language").data("kendoDropDownList");
                if (ddl) {
                    ddl.value(lang);
                    ddl.trigger("change");
                } else {
                    $("#language").val(lang);
                }
            }''', lang_code
        )

    def set_runtime_range(self, min_mins, max_mins):
        self.page.evaluate(
            '''([min, max]) => {
                var slider = $("#runtime_range").data("kendoRangeSlider");
                if (slider) {
                    slider.values(min, max);
                    slider.trigger("change");
                } else {
                    $("#with_runtime_gte").val(min);
                    $("#with_runtime_lte").val(max);
                }
            }''', [min_mins, max_mins]
        )

    def set_availabilities(self, types):
        all_checkbox = self.page.locator("input#all_availabilities")
        is_all_checked = all_checkbox.is_checked()

        if not types:
            if not is_all_checked:
                all_checkbox.click()
            return

        if is_all_checked:
            all_checkbox.click()

        mapping = {
            "flatrate": "input#ott_monetization_type_flatrate",
            "free": "input#ott_monetization_type_free",
            "ads": "input#ott_monetization_type_ads",
            "rent": "input#ott_monetization_type_rent",
            "buy": "input#ott_monetization_type_buy"
        }

        for m_type, css_sel in mapping.items():
            loc = self.page.locator(css_sel)
            should_be_checked = (m_type in types)
            if loc.is_checked() != should_be_checked:
                loc.click()

    def apply_filters(self):
        self.search_button.click()
        self.page.wait_for_timeout(2000) # wait for grid to update

    def get_movie_titles(self):
        if self.movie_titles.count() > 0:
            self.movie_titles.first.wait_for(state="visible", timeout=10000)
        
        import os
        username = os.getenv("TMDB_USERNAME", "")
        
        titles = self.movie_titles.all_inner_texts()
        return [t.strip() for t in titles if t.strip() and t.strip().lower() != username.lower()]
