import pytest
from common.tools import Tools
from playwright.sync_api import Page
from pages.login_page import CinescopeLoginPage
from pages.register_page import CinescopeRegisterPage
from pages.movie_page import CinescopeMoviePage
from utils.data_generator import DataGenerator
from playwright.sync_api import expect

DEFAULT_UI_TIMEOUT = 30000

@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    browser = playwright.chromium.launch()  # headless=True для CI/CD, headless=False для локальной разработки
    yield browser  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    browser.close()  # Браузер закрывается после завершения всех тестов

@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)
    yield context
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir('playwright_trace', log_name)
    context.tracing.stop(path=trace_path)
    context.close()

@pytest.fixture(scope="function")  # Страница создается для каждого теста
def page(context):
    page = context.new_page()
    yield page  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    page.close()  # Страница закрывается после завершения теста

@pytest.fixture
def register_page(page: Page) -> CinescopeRegisterPage:
    register_page = CinescopeRegisterPage(page)
    register_page.open()
    return register_page

@pytest.fixture
def login_page(page: Page) -> CinescopeLoginPage:
    login_page = CinescopeLoginPage(page)
    login_page.open()
    return login_page

@pytest.fixture
def logged_in_user(registered_user, login_page) -> dict:
    login_page.open()
    login_page.login(registered_user["email"], registered_user["password"])
    expect(login_page.page.get_by_role("link", name="Профиль")).to_be_visible(timeout=5000)
    return registered_user

@pytest.fixture
def movie_page(page: Page) -> CinescopeMoviePage:
    return CinescopeMoviePage(page)

@pytest.fixture
def registered_user(api) -> dict:
    user_data = DataGenerator.generate_user_data()
    api.auth.register_user({
        "fullName": user_data["full_name"],
        "email": user_data["email"],
        "password": user_data["password"],
        "passwordRepeat": user_data["password"],
    })
    return user_data
