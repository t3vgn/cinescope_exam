# tests/ui/conftest.py
import pytest
import requests

from playwright.sync_api import Page, expect

from clients.api_manager import ApiManager
from common.tools import Tools
from pages.register_page import CinescopeRegisterPage
from pages.login_page import CinescopeLoginPage
from pages.movie_page import CinescopeMoviePage
from utils.data_generator import DataGenerator
from config.settings import Settings


DEFAULT_UI_TIMEOUT = 30_000


# ============================================================
# Браузер и контекст
# ============================================================

@pytest.fixture(scope="session")
def browser(playwright):
    browser = playwright.chromium.launch(headless=False)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)
    yield context
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir("playwright_trace", log_name)
    context.tracing.stop(path=trace_path)
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()


# ============================================================
# Page Objects
# ============================================================

@pytest.fixture
def register_page(page: Page) -> CinescopeRegisterPage:
    register_page = CinescopeRegisterPage(page)
    register_page.open()
    return register_page


@pytest.fixture
def login_page(page: Page) -> CinescopeLoginPage:
    return CinescopeLoginPage(page)


@pytest.fixture
def movie_page(page: Page) -> CinescopeMoviePage:
    return CinescopeMoviePage(page)


# ============================================================
# Пользователи
# ============================================================

@pytest.fixture
def registered_user(register_page) -> dict:
    """Регистрация через UI-форму (как было в exam_module_7)."""
    user_data = DataGenerator.generate_user_data()
    register_page.register(
        user_data["full_name"],
        user_data["email"],
        user_data["password"],
    )
    return user_data


@pytest.fixture
def logged_in_user(registered_user, login_page) -> dict:
    #login_page.open()
    login_page.login(
        registered_user["email"],
        registered_user["password"],
    )
    expect(
        login_page.page.get_by_role("link", name="Профиль")
    ).to_be_visible(timeout=5000)
    return registered_user


# ============================================================
# Фильм — через API (чтобы не зависеть от API-фикстур)
# ============================================================

@pytest.fixture
def created_movie() -> dict:
    """Создаёт фильм ЧЕРЕЗ API — нужен для UI-теста отзыва."""
    session = requests.Session()
    api = ApiManager(session=session)

    login = api.auth.login_user({
        "email": Settings.ADMIN_EMAIL,
        "password": Settings.ADMIN_PASSWORD,
    })
    api.set_token(login.json()["accessToken"])

    movie_data = DataGenerator.generate_movie_payload()
    movie = api.movies.create_movie(movie_data).json()

    yield {"id": movie["id"], "data": movie_data}

    try:
        api.movies.delete_movie(movie["id"])
    finally:
        session.close()