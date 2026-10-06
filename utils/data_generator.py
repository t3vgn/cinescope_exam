# utils/data_generator.py
from random import randint



class DataGenerator:

    @staticmethod
    def generate_email() -> str:
        return f"aqatest{randint(1, 999999)}@email.qa"

    @staticmethod
    def generate_full_name() -> str:
        return "Иван Иванов"

    @staticmethod
    def generate_password() -> str:
        return "qwerty123Q"

    @staticmethod
    def generate_review_text() -> str:
        return f"Отличный фильм! Смотрели всей семьей. Отзыв #{randint(1, 9999)}"

    @classmethod
    def generate_user_data(cls) -> dict:
        return {
            "full_name": cls.generate_full_name(),
            "email": cls.generate_email(),
            "password": cls.generate_password(),
        }

