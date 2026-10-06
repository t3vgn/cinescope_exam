from pages.base_page import BasePage
from playwright.sync_api import expect

class CinescopeMoviePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = f"{self.home_url}movies"

        self.review_input = '[data-qa-id="movie_review_input"]'
        self.submit_review_button = '[data-qa-id="movie_review_submit_button"]'
        self.rating_combobox = '[data-qa-id="movie_rating_select"]'

    def open_movie(self, movie_id: int):
        expected_url = f"{self.url}/{movie_id}"
        self.open_url(expected_url)
        expect(self.page).to_have_url(expected_url)
        expect(self.page.locator(self.review_input)).to_be_visible()

    def select_rating(self, rating: str):
        self.page.locator(self.rating_combobox).click(force=True)
        self.page.get_by_role("option", name=rating).click()

    def leave_review(self, text: str, rating: str = "5"):
        self.enter_text(self.review_input, text)
        self.select_rating(rating)
        self.click(self.submit_review_button)