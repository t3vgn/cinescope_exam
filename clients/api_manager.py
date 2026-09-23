import requests
from clients.custom_requester import CustomRequester
from config.base_urls import AUTH_BASE_URL, API_BASE_URL


class AuthApi(CustomRequester):
    """API авторизации"""

    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def register_user(self, user_data, expected_status=201):
        return self.send_request(
            "POST", "/register", data=user_data, expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=200):
        return self.send_request(
            "POST", "/login", data=login_data, expected_status=expected_status
        )


class MoviesApi(CustomRequester):
    """API фильмов"""

    def __init__(self, session):
        super().__init__(session=session, base_url=API_BASE_URL)

    def get_movies(self, params=None, expected_status=200):
        return self.send_request(
            "GET", "/movies", params=params, expected_status=expected_status
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        return self.send_request(
            "GET", f"/movies/{movie_id}", expected_status=expected_status
        )

    def create_movie(self, movie_data, expected_status=201):
        return self.send_request(
            "POST", "/movies", data=movie_data, expected_status=expected_status
        )

    def patch_movie(self, movie_id, patch_data, expected_status=200):
        return self.send_request(
            "PATCH", f"/movies/{movie_id}",
            data=patch_data, expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        return self.send_request(
            "DELETE", f"/movies/{movie_id}", expected_status=expected_status
        )


class ApiManager:
    """Менеджер всех API-клиентов с общей сессией"""

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.auth = AuthApi(self.session)
        self.movies = MoviesApi(self.session)

    def set_token(self, token: str):
        """Добавляет токен в заголовки сессии"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def close(self):
        self.session.close()