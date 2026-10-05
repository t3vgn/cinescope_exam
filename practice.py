from playwright.sync_api import Page, expect
from random import randint
import time


def test_text_box(page: Page):
    # page.goto('https://dev-cinescope.coconutqa.ru/register')

    page.goto("https://demoqa.com/text-box")
    page.get_by_role("textbox", name="Full Name").fill("Жмых Жмыхович Жмышенко")
    page.get_by_role("textbox", name="name@example.com").fill("test123312@mail.ru")
    page.get_by_role("textbox", name="Current Address").fill("Russia, SPB")
    page.locator("#permanentAddress").fill("Kyrgyzstan, Bishkek")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Name:Жмых Жмыхович Жмышенко")).to_be_visible()
    expect(page.get_by_text("Email:test123312@mail.ru")).to_be_visible()
    expect(page.get_by_text("Current Address :Russia, SPB")).to_be_visible()
    expect(page.get_by_text("Permananet Address :")).to_be_visible()

    time.sleep(10)
    '''
    user_email = f'test{randint(1, 9999)}-admin@email.qa'
    page.locator('[data-qa-id="register_full_name_input"]').fill('Жмых Жмыхович Жмышенко')
    page.locator('[data-qa-id="register_email_input"]').fill(user_email)
    page.locator('[data-qa-id="register_password_input"]').fill('TestQA1234')
    page.locator('[data-qa-id="register_password_repeat_input"]').fill('TestQA1234')
    page.click('[data-qa-id="register_submit_button"]')

    page.wait_for_url('https://dev-cinescope.coconutqa.ru/login')
    expect(page.get_by_text("Подтвердите свою почту")).to_be_visible(visible=True)
    time.sleep(10)
    '''

