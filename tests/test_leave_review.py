import allure
import pytest
from playwright.sync_api import expect

from utils.data_generator import DataGenerator

@allure.epic("Тестирование UI")
@allure.feature("Отзывы")
@pytest.mark.ui
class TestMovieReview:

    @allure.title("Оставление отзыва под фильмом")
    def test_leave_review(self, logged_in_user, movie_page, page):
        review_text = DataGenerator.generate_review_text()

        movie_page.open_movie(movie_id=70511)

        # Передаём и текст, и оценку
        movie_page.leave_review(review_text, rating="5")

        expect(page.get_by_text(review_text)).to_be_visible()