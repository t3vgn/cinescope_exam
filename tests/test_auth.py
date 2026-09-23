import pytest
from data.auth.register_data import get_register_payload
from utils.data_generator import DataGenerator


@pytest.mark.api
class TestAuthPositive:

    def test_register_user(self, api):
        """Позитивный: регистрация нового пользователя"""
        user_data = get_register_payload()
        response = api.auth.register_user(user_data)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_login_registered_user(self, api):
        """Позитивный: логин зарегистрированного пользователя"""
        user_data = get_register_payload()
        api.auth.register_user(user_data)
        response = api.auth.login_user({
            "email": user_data["email"],
            "password": user_data["password"],
        })
        assert response.status_code == 200
        assert "accessToken" in response.json()


@pytest.mark.api
class TestAuthNegative:

    def test_login_with_invalid_password(self, api):
        """Негативный: логин с неверным паролем → 401"""
        # 1. Регистрируем пользователя
        user_data = get_register_payload()
        api.auth.register_user(user_data)

        # 2. Пытаемся залогиниться с неверным паролем
        # ✅ ИСПОЛЬЗУЕМ send_request, а не login_user
        response = api.auth.send_request(
            "POST", "/login",
            data={
                "email": user_data["email"],
                "password": "WrongPassword123!",
            },
            expected_status=401   # ← ОЖИДАЕМ 401!
        )

        # 3. Проверяем
        assert response.status_code == 401
        body = response.json()
        assert "accessToken" not in body
        assert body["message"] == "Неверный логин или пароль"