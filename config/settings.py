# config/settings.py
import os
from dotenv import load_dotenv
load_dotenv()


class Settings:
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")

    @classmethod
    def validate(cls):
        if not cls.ADMIN_EMAIL:
            raise ValueError("ADMIN_EMAIL не задан в .env")
        if not cls.ADMIN_PASSWORD:
            raise ValueError("ADMIN_PASSWORD не задан в .env")


# Проверяем при импорте
Settings.validate()