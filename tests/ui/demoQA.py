#test_demoQA.py
import allure
from playwright.sync_api import Page, expect
import time
import pytest
from datetime import datetime
import re

class TestDemoQAForm:
    def test_fill_registration_form(self, page: Page):
        with allure.step("Открываем страницу DemoQA"):
            page.goto("https://demoqa.com/webtables")

        with allure.step("Кликаем кнопку 'Add' через CSS-селектор"):
            page.locator("button:has-text('Add')").click()

        with allure.step("Ждём, что модальное окно с формой открылось"):
            # Модальное окно регистрации
            registration_form = page.locator("#registration-form-modal")
            registration_form.wait_for(state="visible")
            assert registration_form.is_visible(), "Модальное окно регистрации не открылось"

        with allure.step("Проверяем заголовок модального окна"):
            expect(registration_form).to_contain_text("Registration Form")

        with allure.step("Заполняем First Name через placeholder"):
            first_name_input = page.locator("input[placeholder='First Name']")
            first_name_input.fill("Иван")

        with allure.step("Заполняем остальные поля"):

            page.locator("input[placeholder='Last Name']").fill("Иванов")

            page.locator("input[placeholder='name@example.com']").fill("ivan@mail.ru")

            page.locator("input[placeholder='Age']").fill("23")

            page.locator("input[placeholder='Salary']").fill("250000")

            page.locator("input[placeholder='Department']").fill("QA")

        with allure.step("Нажимаем Submit"):
            submit_button = page.locator("button:has-text('Submit')")
            submit_button.click()
        time.sleep(10)

    @allure.story("Полное заполнение формы")
    @allure.title("Заполнение Practice Form со всеми типами полей")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_automation_practice_form(self, page: Page):
        with allure.step("Открываеем страницу DemoQA"):
            page.goto("https://demoqa.com/automation-practice-form")

        with allure.step("Заполняем поля:"):
            first_name = page.locator("#firstName")
            first_name.fill("Иван")
            assert first_name.input_value() == "Иван"

        with allure.step("Заполняем Last Name через type()"):
            last_name = page.locator("#lastName")
            last_name.type("Иванов", delay=100)
            assert last_name.input_value() == "Иванов"

        with allure.step("Заполняем Email через type()"):
            email = page.locator("#userEmail")
            email.type("ivan@mail.ru", delay=50)
            assert email.input_value() == "ivan@mail.ru"

        with allure.step("Выбираем Gender = Male (радиобатон)"):
            page.get_by_label("Male", exact=True).check()
            assert page.locator("#gender-radio-1").is_checked()

        with allure.step("Заполняем Mobile через type()"):
            mobile = page.locator("#userNumber")
            mobile.fill("8999999999")
            assert mobile.input_value() == "8999999999"

        with allure.step("Выбираем Subjects через автокомплит"):
            subjects = page.locator("#subjectsInput")
            subjects.fill("Math")
            page.locator(".subjects-auto-complete__option").first.click()

        with allure.step("Выбираем hobbies через чекбоксы"):
            page.get_by_label("Sports").check()
            page.get_by_label("Reading").check()
            assert page.locator("#hobbies-checkbox-1").is_checked()
            assert page.locator("#hobbies-checkbox-2").is_checked()
            assert not page.locator("#hobbies-checkbox-3").is_checked()

        with allure.step("Загружаем файл (Upload Picture)"):
            page.locator("#uploadPicture").set_input_files({
                "name": "test.txt",
                "mimeType": "text/plain",
                "buffer": b"hello world",
            })

        with allure.step("Заполняем Current Address"):
            page.locator("#currentAddress").fill("г. Москва, ул. Пушкина, д. 1")

        with allure.step("Выбираем State (выпадающий список)"):
            page.locator("#state").click()
            page.locator("#react-select-3-option-0").click()

        with allure.step("Выбираем City"):
            page.locator("#city").click()
            page.locator("#react-select-4-option-0").click()

        with allure.step("Проверяем, что Date of Birth по умолчанию == сегодня"):
            date_input = page.locator("#dateOfBirthInput")
            actual_value = date_input.get_attribute("value")
            expected_value = datetime.now().strftime("%d %b %Y")
            assert actual_value == expected_value, (
                f"Значение Date of Birth: ожидали '{expected_value}' (сегодня), "
                f"получили '{actual_value}'"
            )

        with allure.step("Нажимаем Submit"):
            page.locator("#submit").click()

        with allure.step("Проверяем, что модалка с результатом открылась"):
            result_modal = page.locator(".modal-content")
            expect(result_modal).to_be_visible()

        with allure.step("Проверяем, что в результате есть наши данные"):
            expect(result_modal).to_contain_text("Иван")
            expect(result_modal).to_contain_text("Иванов")
            expect(result_modal).to_contain_text("ivan@mail.ru")
        time.sleep(10)

@allure.epic("UI тесты")
@allure.feature("DEMOQA — Проверки")
class TestDemoQAFooter:

    URL = "https://demoqa.com/automation-practice-form"

    @allure.story("Проверка футера")
    @allure.title("Текст футера совпадает с ожидаемым")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_footer_text(self, page: Page):
        with allure.step("Открываем страницу"):
            page.goto(self.URL)

        with allure.step("Достаём текст футера"):
            footer = page.locator("footer")
            footer_text = footer.text_content().strip()
            # Например: "© 2013-2026 TOOLSQA.COM | ALL RIGHTS RESERVED."

        with allure.step("Проверяем, что текст футера совпадает"):
            # Проверяем через регулярку — год может меняться
            assert re.match(
                r"©\s*\d{4}-\d{4}\s+TOOLSQA\.COM\s*\|\s*ALL RIGHTS RESERVED\.",
                footer_text,
            ), f"Футер не совпадает. Получено: '{footer_text}'"

@allure.epic("UI тесты")
@allure.feature("DEMOQA — Radio Button")
class TestDemoQARadioButton:

    URL = "https://demoqa.com/radio-button"

    @allure.story("Проверка активности радиобаттонов")
    @allure.title("Два радиобаттона активны, третий — disabled")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_radio_buttons_state(self, page: Page):
        with allure.step("Ожидаем полную загрузку страницы"):
            page.wait_for_load_state('load')

        with allure.step("Открываем страницу Radio Button"):
            page.goto(self.URL)

        with allure.step("Yes активен:"):
            yes_radio = page.locator("#yesRadio")
            assert yes_radio.is_enabled(), "Yes должен быть активен"
            assert yes_radio.is_editable(), "Yes должен быть активен для клика"

        with allure.step("Impressive активен:"):
            impressive_radio = page.locator("#impressiveRadio")
            assert impressive_radio.is_enabled(), "Impressive должен быть активен"
            assert impressive_radio.is_editable(), "Impressive должен быть активен для клика"

        with allure.step("No неактивен:"):
            no_radio = page.locator("#noRadio")
            assert no_radio.is_disabled(), "No должна быть неактивна"
            assert not no_radio.is_editable(), "No должна быть некликабельна"

        with allure.step("Кликем Yes, проверяем что выбрана"):
            yes_radio.check()
            assert yes_radio.is_checked(), "Yes должен быть выбран"
            time.sleep(3)

        with allure.step("Проверяем, что появилось сообщение о выборе Yes"):
            expect(page.locator(".text-success")).to_have_text("Yes")

        with allure.step("Кликаем Impressive, проверяем что выбрана"):
            impressive_radio.check()
            assert impressive_radio.is_checked(), "Impressive должна быть выбрана"

        with allure.step("Проверяем, что появилось сообщение о выборе Impressive"):
            expect(page.locator(".text-success")).to_have_text("Impressive")

        with allure.step("Пытаемся кликнуть No — ничего не меняется"):
            no_radio.click(force=True)
            assert not no_radio.is_checked(), "No не должен стать выбранным — он disabled"
            assert impressive_radio.is_checked(), "Impressive должен остаться выбранным"

        with allure.step("Проверяем, что сообщение не изменилось"):
            expect(page.locator(".text-success")).to_have_text("Impressive")
        time.sleep(10)

@allure.epic("UI тесты")
@allure.feature("DEMOQA — Check Box")
class TestDemoQACheckBox:
    URL = "https://demoqa.com/checkbox"
    @allure.story("Дерево чекбоксов")
    @allure.title("Home виден, Desktop скрыт, после раскрытия — Desktop виден")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_is_visible_home_and_desktop(self, page: Page):
        with allure.step("Открываем Check Box"):
            page.goto(self.URL)
            home = page.get_by_role("treeitem", name="Home")
            desktop = page.get_by_role("treeitem", name="Desktop")

        with allure.step("Проверяем что Home виден"):
            expect(home).to_be_visible()

        with allure.step("Проверяем, что Desktop не виден (дерево свёрнуто)"):
            expect(desktop).not_to_be_visible()

        with allure.step("Кликаем по свитчеру Home, чтобы раскрыть дерево"):
            home.locator(".rc-tree-switcher").click()

        with allure.step("Проверяем, что Desktop стал виден"):
            expect(desktop).to_be_visible()

        with allure.step("Проверяем, что Home остался виден"):
            expect(home).to_be_visible()
        time.sleep(5)

class TestDemoQADynamicProperties:

    URL = "https://demoqa.com/dynamic-properties"

    @allure.story("Динамические свойства")
    @allure.title("Кнопка 'Visible After 5 Seconds' появляется с задержкой")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_visible_after_five_seconds(self, page: Page):
        with allure.step("Открываем страницу Dynamic Properties"):
            page.goto(self.URL)

        with allure.step("Проверяем, что кнопка 'Visible After 5 Seconds' отсутствует в DOM"):
            assert not page.locator("#visibleAfter").is_visible(), "Элемент не должен оторбражаться на странице"

        with allure.step("Дожидаемся появления кнопки через page.wait_for_selector()"):
            page.wait_for_selector("#visibleAfter", state="visible", timeout=6000)

        with allure.step("Проверяем, что кнопка теперь видна"):
            visible_after_button = page.locator("#visibleAfter")
            expect(visible_after_button).to_be_visible()
            expect(visible_after_button).to_be_enabled()
            time.sleep(5)

    def test_expect(self, page: Page):
        page.goto("https://demoqa.com/radio-button")
        yes_radio = page.get_by_role("radio", name="Yes")
        impressive_radio = page.get_by_role("radio", name="Impressive")
        no_radio = page.get_by_role("radio", name="No")
        expect(no_radio).to_be_disabled()  # проверяем, что не доступен
        expect(yes_radio).to_be_enabled()  # проверяем, что доступен
        expect(impressive_radio).to_be_enabled()  # проверяем, что доступен
        page.locator(
            '[for="yesRadio"]').click()  # тут хитрый лейбл не позволяет кликнуть прямо на инпут, обращаемся по лейблу
        expect(yes_radio).to_be_checked()  # проверяем, что отмечен
        expect(impressive_radio).not_to_be_checked()
        time.sleep(5)