import pytest
import requests
import time
from clients.api_manager import ApiManager
from config.settings import Settings
from entities.user import User
from utils.data_generator import DataGenerator
from constants.roles import Roles
from data.auth.register_data import get_register_payload
from models.base_models import TestUser

from sqlalchemy.orm import Session
from resources.db_client import get_db_session
from utils.db_helpers import DBHelper


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


@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        Settings.ADMIN_EMAIL,
        Settings.ADMIN_PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()
    """Базовые данные пользователя"""
    return TestUser(
        email = DataGenerator.generate_random_email(),
        fullName = DataGenerator.generate_random_name(),
        password = random_password,
        passwordRepeat = random_password,
        roles = [Roles.USER],
    )

@pytest.fixture(scope="function")
def creation_user_data(test_user: TestUser) -> TestUser:
    return test_user.model_copy(update={"verified": True, "banned": False})


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data ) -> User:
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)

    common_user.api.auth.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def admin_user(user_session, super_admin):
    new_session = user_session()

    random_password = DataGenerator.generate_random_password()
    admin_data = {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.ADMIN.value],
        "verified": True,
        "banned": False,
    }

    admin_user = User(
        admin_data["email"],
        admin_data["password"],
        [Roles.ADMIN.value],
        new_session,
    )

    super_admin.api.user_api.create_user(admin_data)
    admin_user.api.auth.authenticate(admin_user.creds)
    return admin_user


@pytest.fixture(scope="function")
def user_with_role(api):

    created_tokens = []

    def _create(role: str) -> str:
        if role == "SUPER_ADMIN":
            login_data = {
                "email": "api1@gmail.com",
                "password": "asdqwe123Q",
            }
            response = api.auth.login_user(login_data, expected_status=200)
            return response.json()["accessToken"]


        user_data = get_register_payload(roles=[role])
        api.auth.register_user(user_data)
        login = api.auth.login_user({
            "email": user_data["email"],
            "password": user_data["password"],
        })
        return login.json()["accessToken"]

    return _create

@pytest.fixture(scope="module")
def db_session() -> Session:

    db_session = get_db_session()
    yield db_session
    db_session.close()


@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:

    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):

    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)

@pytest.fixture
def delay_between_retries():
    time.sleep(2)
    yield