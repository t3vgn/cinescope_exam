import pytest
import requests
from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator
from config.settings import Settings


@pytest.fixture(scope="session")
def session():
    return requests.Session()


@pytest.fixture(scope="session")
def api(session):
    manager = ApiManager(session=session)
    yield manager
    manager.close()


@pytest.fixture(scope="function")
def super_admin_token(api):
    response = api.auth.login_user({
        "email": Settings.ADMIN_EMAIL,
        "password": Settings.ADMIN_PASSWORD,
    })
    return response.json()["accessToken"]


@pytest.fixture(scope="function")
def authorized_api(api, super_admin_token):
    api.set_token(super_admin_token)
    yield api
    # Очистка: убираем токен после теста
    api.session.headers.pop("Authorization", None)


@pytest.fixture(scope="function")
def unauthorized_api():
    session = requests.Session()
    api = ApiManager(session=session)
    yield api
    session.close()


@pytest.fixture(scope="function")
def created_movie(authorized_api):
    movie_data = DataGenerator.generate_movie_payload()
    response = authorized_api.movies.create_movie(movie_data)
    movie_id = response.json()["id"]

    yield {"id": movie_id, "data": movie_data}

    authorized_api.movies.delete_movie(movie_id)