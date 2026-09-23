import pytest
import requests
from clients.api_manager import ApiManager
from data.auth.register_data import get_register_payload
from utils.data_generator import DataGenerator


@pytest.fixture(scope="session")
def session():
    return requests.Session()


@pytest.fixture(scope="session")
def api(session):
    """Менеджер API — общий для всей сессии"""
    manager = ApiManager(session=session)
    yield manager
    manager.close()


@pytest.fixture(scope="function")
def super_admin_token(api):
    login_data = {
        "email": "api1@gmail.com",       # ← из документации
        "password": "asdqwe123Q",
    }
    response = api.auth.login_user(login_data, expected_status=200)
    return response.json()["accessToken"]


@pytest.fixture(scope="function")
def authorized_api(api, super_admin_token):
    """API с установленным токеном авторизации"""
    api.set_token(super_admin_token)
    yield api
    # Очистка: убираем токен после теста
    api.session.headers.pop("Authorization", None)


@pytest.fixture(scope="function")
def created_movie(authorized_api):
    """Создаёт фильм и удаляет его после теста (teardown)"""
    movie_data = DataGenerator.generate_movie_payload()
    response = authorized_api.movies.create_movie(movie_data)
    movie_id = response.json()["id"]

    yield {"id": movie_id, "data": movie_data}

    # Teardown: удаляем фильм, если ещё существует
    try:
        authorized_api.movies.delete_movie(movie_id)
    except Exception:
        pass