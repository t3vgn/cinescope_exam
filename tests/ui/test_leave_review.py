#test_leave_review.py
import allure
import pytest
from playwright.sync_api import expect

from tests.conftest import created_movie
from utils.data_generator import DataGenerator

@allure.epic("Тестирование UI")
@allure.feature("Отзывы")
@pytest.mark.ui
class TestMovieReview:

    @allure.title("Оставление отзыва под фильмом")
    def test_leave_review(self, logged_in_user, movie_page, page, created_movie):
        review_text = DataGenerator.generate_review_text()
        movie_id = created_movie["id"]
        movie_page.open_movie(movie_id=movie_id)
        movie_page.leave_review(review_text, rating="5")

        expect(page.get_by_text(review_text)).to_be_visible()