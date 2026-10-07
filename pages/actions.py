# pages/actions.py
import allure
from playwright.sync_api import Page

class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста в поле: {locator}")
    def enter_text(self, locator: str, text: str):
        element = self.page.locator(locator)
        element.click()  # фокус
        element.press_sequentially(text, delay=30)

    @allure.step("Клик по элементу: {locator}")
    def click(self, locator: str):
        self.page.click(locator)