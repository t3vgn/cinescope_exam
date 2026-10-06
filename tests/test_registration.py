import allure
import pytest

from playwright.sync_api import Page, expect
from utils.data_generator import DataGenerator

@allure.epic("Тестирование UI")
@allure.feature("Регистрация")
@pytest.mark.ui
class TestRegistration:

    @allure.title("Успешная регистрация нового пользователя")
    def test_registration(self, register_page, page):
        user_data = DataGenerator.generate_user_data()

        register_page.register(
            user_data["full_name"],
            user_data["email"],
            user_data["password"],
        )
        expect(page.get_by_text("Подтвердите свою почту")).to_be_visible()