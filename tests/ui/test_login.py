#test_login.py
import allure
import pytest
from playwright.sync_api import expect


@allure.epic("Тестирование UI")
@allure.feature("Авторизация")
@pytest.mark.ui
class TestLogin:

    @allure.title("Успешный вход ранее зарегистрированного пользователя")
    def test_login(self, login_page, registered_user, page):
        login_page.login(
            registered_user["email"],
            registered_user["password"],
        )

        expect(page).to_have_url("https://dev-cinescope.coconutqa.ru/")
        expect(page.get_by_text("Вы вошли в аккаунт")).to_be_visible()
