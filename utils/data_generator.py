# utils/data_generator.py
import re
import uuid
import requests
from faker import Faker

faker = Faker("ru_RU")


class DataGenerator:

    @staticmethod
    def generate_random_email() -> str:
        return f"user.{uuid.uuid4().hex[:8]}@mail.ru"

    @staticmethod
    def generate_random_name() -> str:
        """ФИО: только буквы (без ё/Ё) и пробелы"""
        name = faker.name()
        # Заменяем ё → е
        name = name.replace("ё", "е").replace("Ё", "Е")
        # Убираем всё, кроме букв и пробелов
        name = re.sub(r"[^A-Za-zА-Яа-я\s]", "", name)
        return name.strip()

    @staticmethod
    def generate_random_password() -> str:
        return "Test1234!"

    @staticmethod
    def get_valid_genre_id() -> int:
        response = requests.get(
            "https://api.dev-cinescope.coconutqa.ru/genres"
        )
        return response.json()[0]["id"]

    @staticmethod
    def generate_movie_patch_data() -> dict:
        """Данные для частичного обновления фильма"""
        return {
            "name": f"Обновлённый фильм {uuid.uuid4().hex[:8]}",
            "price": 1500,
        }

    @staticmethod
    def generate_movie_payload(
        name: str = None,
        image_url: str = "https://picsum.photos/200/300",
        price: int = 100,
        description: str = None,
        location: str = "SPB",
        published: bool = True,
        genre_id: int = None,
    ) -> dict:
        if not name or not isinstance(name, str) or not name.strip():
            name = f"Фильм {uuid.uuid4().hex[:8]}"

        if not description:
            description = "Описание тестового фильма"

        if genre_id is None:
            genre_id = DataGenerator.get_valid_genre_id()

        return {
            "name": name,
            "imageUrl": image_url,
            "price": price,
            "description": description,
            "location": location,
            "published": published,
            "genreId": genre_id,
        }