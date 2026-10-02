import pytest
import allure
from sqlalchemy.orm import Session

from db_models.accounts import AccountTransactionTemplate
from utils.data_generator import DataGenerator


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountTransactionTemplate:

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.description("""
        Этот тест проверяет, что перевод не проходит, если у отправителя недостаточно средств.
        Шаги:
        1. Создание двух счетов: Stan и Bob.
        2. Попытка перевода 200 единиц от Stan к Bob (у Stan только 100).
        3. Проверка, что балансы не изменились.
        4. Очистка тестовых данных.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Eugene Te")
    @allure.title("Тест перевода денег между счетами: недостаточно средств")
    def test_transfer_insufficient_funds(self, db_session: Session):

        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(
                user=f"Stan_{DataGenerator.generate_random_int(10)}",
                balance=100,
            )
            bob = AccountTransactionTemplate(
                user=f"Bob_{DataGenerator.generate_random_int(10)}",
                balance=500,
            )
            db_session.add_all([stan, bob])
            db_session.commit()

        @allure.step("Функция перевода денег: transfer_money")
        def transfer_money(session, from_account, to_account, amount):
            with allure.step("Получаем счета"):
                src = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                dst = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step("Проверяем, что на счете достаточно средств"):
                if src.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                src.balance -= amount
                dst.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()

        try:
            with allure.step("Проверяем начальные балансы"):
                assert stan.balance == 100
                assert bob.balance == 500

            with allure.step("Пытаемся перевести 200 (больше, чем есть у Stan)"):
                with pytest.raises(ValueError, match="Недостаточно средств"):
                    transfer_money(
                        db_session,
                        from_account=stan.user,
                        to_account=bob.user,
                        amount=200,
                    )

            with allure.step("Проверяем, что в БД балансы не изменились"):
                db_session.rollback()

                stan_db = (
                    db_session.query(AccountTransactionTemplate)
                    .filter_by(user=stan.user)
                    .one()
                )
                bob_db = (
                    db_session.query(AccountTransactionTemplate)
                    .filter_by(user=bob.user)
                    .one()
                )
                assert stan_db.balance == 100, "Деньги Стена не должны были измениться"
                assert bob_db.balance == 500, "Деньги Боба не должны были измениться"

        finally:
            with allure.step("Удаляем тестовые данные"):
                db_session.rollback()
                db_session.query(AccountTransactionTemplate).filter(
                    AccountTransactionTemplate.user.in_([stan.user, bob.user])
                ).delete(synchronize_session=False)
                db_session.commit()