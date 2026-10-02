import pytest
import allure
import requests
import time
import logging
from clients.api_manager import ApiManager
from config.settings import Settings
from entities.user import User
from constants.roles import Roles
from models.base_models import UserData
from db_requester.db_client import get_db_session
from utils.db_helpers import DBHelper
from models.movies_models import MovieResponse
from utils.data_generator import DataGenerator

logger = logging.getLogger(__name__)
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
def test_user() -> UserData:
    random_password = DataGenerator.generate_random_password()
    """Базовые данные пользователя"""
    return UserData(
        email = DataGenerator.generate_random_email(),
        fullName = DataGenerator.generate_random_name(),
        password = random_password,
        passwordRepeat = random_password,
        roles = [Roles.USER],
    )

@pytest.fixture(scope="function")
def creation_user_data(test_user: UserData) -> UserData:
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
def user_with_role(api, super_admin):
    """
    Фабрика: создаёт пользователя, меняет ему роль через PATCH /user/{id}
    под супер-админом, возвращает токен и роли из ответа логина.
    """
    created_users = []

    def _create(role: str) -> dict:
        if role == "SUPER_ADMIN":
            login_data = {
                "email": Settings.ADMIN_EMAIL,
                "password": Settings.ADMIN_PASSWORD,
            }
            response = api.auth.login_user(login_data, expected_status=200)
            body = response.json()
            return {
                "accessToken": body["accessToken"],
                "roles": body["user"]["roles"],
                "email": login_data["email"],
            }

        email = DataGenerator.generate_random_email()
        password = DataGenerator.generate_random_password()
        user_data = UserData(
            email=email,
            fullName=DataGenerator.generate_random_name(),
            password=password,
            passwordRepeat=password,
            roles=[Roles.USER],
        )
        super_admin.api.user_api.create_user(user_data)

        user_response = super_admin.api.user_api.get_user_by_email(email)
        user_id = user_response.json()["id"]
        created_users.append(user_id)

        super_admin.api.user_api.patch_user(
            user_id,
            {"roles": [role]},
        )

        login = api.auth.login_user({
            "email": email,
            "password": password,
        }, expected_status=200)
        body = login.json()

        return {
            "accessToken": body["accessToken"],
            "roles": body["user"]["roles"],
            "email": email,
        }

    yield _create

    for user_id in created_users:
        try:
            super_admin.api.user_api.delete_user(user_id)
        except Exception as e:
            logger.warning(
                f"Cleanup не удался для user_id={user_id}: "
                f"{type(e).__name__}: {e}"
            )

@pytest.fixture(scope="function")
def db_session():
    session = get_db_session()
    yield session
    session.rollback()


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

@pytest.fixture(scope="function")
def movie_by_super_admin(api, super_admin):
    with allure.step("Создаём фильм под SUPER_ADMIN"):
        # SUPER_ADMIN уже логинен в super_admin.api
        movie_data = DataGenerator.generate_movie_payload()
        create_response = super_admin.api.movies.create_movie(movie_data)
        assert create_response.status_code == 201, (
            f"Не удалось создать фильм: {create_response.status_code} "
            f"{create_response.text}"
        )
        created = MovieResponse.model_validate(create_response.json())

    yield created

    with allure.step("Cleanup: удаляем фильм под SUPER_ADMIN"):
        try:
            super_admin.api.movies.delete_movie(created.id)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"Cleanup фильма id={created.id} не удался: {e}"
            )