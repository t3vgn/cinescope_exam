import pytest
from utils.data_generator import DataGenerator


@pytest.mark.api
class TestMoviesPositive:

    def test_get_movies_list(self, api):
        """Позитивный: получение списка фильмов"""
        response = api.movies.get_movies()
        assert response.status_code == 200
        data = response.json()
        assert "movies" in data
        assert isinstance(data["movies"], list)

    def test_get_movies_with_filter_min_price(self, api):
        """Позитивный: фильтр по минимальной цене"""
        params = {"page": 1, "pageSize": 10, "minPrice": 500}
        response = api.movies.get_movies(params=params)
        assert response.status_code == 200
        movies = response.json()["movies"]
        for movie in movies:
            assert movie["price"] >= 500
            assert movie["price"] <= 1000

    def test_get_movies_with_filter_location(self, api):
        """Позитивный: фильтр по локации"""
        params = {"page": 1, "pageSize": 10, "locations": ["MSK"]}
        response = api.movies.get_movies(params=params)
        assert response.status_code == 200
        for movie in response.json()["movies"]:
            assert movie["location"] == "MSK"

    def test_get_movie_by_id(self, authorized_api, created_movie):
        """Позитивный: получение фильма по ID"""
        response = authorized_api.movies.get_movie_by_id(created_movie["id"])
        assert response.status_code == 200
        assert response.json()["id"] == created_movie["id"]

    def test_create_movie(self, authorized_api):
        """Позитивный: создание фильма"""
        movie_data = DataGenerator.generate_movie_payload()
        print(f"\n📦 PAYLOAD: {movie_data}")

        response = authorized_api.movies.create_movie(movie_data)
        assert response.status_code == 201

        body = response.json()
        assert body["name"] == movie_data["name"]
        assert body["price"] == movie_data["price"]
        assert "id" in body

        # Cleanup
        authorized_api.movies.delete_movie(body["id"])

    def test_patch_movie(self, authorized_api, created_movie):
        """Позитивный: частичное обновление фильма"""
        patch_data = DataGenerator.generate_movie_patch_data()
        response = authorized_api.movies.patch_movie(
            created_movie["id"], patch_data
        )
        assert response.status_code == 200
        assert response.json()["name"] == patch_data["name"]

    def test_delete_movie(self, authorized_api):
        """Позитивный: удаление фильма"""
        movie_data = DataGenerator.generate_movie_payload()
        created = authorized_api.movies.create_movie(movie_data).json()

        response = authorized_api.movies.delete_movie(created["id"])
        assert response.status_code == 200

        # Проверяем, что фильма больше нет
        authorized_api.movies.send_request(
            "GET", f"/movies/{created['id']}", expected_status=404
        )


@pytest.mark.api
class TestMoviesNegative:

    def test_get_movie_by_nonexistent_id(self, api):
        """Негативный: получение несуществующего фильма"""
        api.movies.send_request(
            "GET", "/movies/99999999", expected_status=404
        )

    def test_create_movie_without_auth(self, api):
        """Негативный: создание фильма без токена"""
        movie_data = DataGenerator.generate_movie_payload()
        api.movies.send_request(
            "POST", "/movies", data=movie_data, expected_status=401
        )

    def test_create_movie_without_required_field(self, authorized_api):
        """Негативный: создание фильма без обязательного поля name"""
        invalid_data = {
            "price": 500,
            "description": "No name",
            "location": "MSK",
            "published": True,
            "genreId": 1,
            "imageUrl": "https://example.com/img.png",
        }
        authorized_api.movies.send_request(
            "POST", "/movies", data=invalid_data, expected_status=400
        )

    def test_delete_movie_without_auth(self, api, authorized_api, created_movie):
        """Негативный: удаление фильма без токена"""
        # Убираем токен
        api.session.headers.pop("Authorization", None)
        api.movies.send_request(
            "DELETE", f"/movies/{created_movie['id']}", expected_status=401
        )

    def test_patch_nonexistent_movie(self, authorized_api):
        """Негативный: обновление несуществующего фильма"""
        patch_data = DataGenerator.generate_movie_patch_data()
        authorized_api.movies.send_request(
            "PATCH", "/movies/99999999",
            data=patch_data, expected_status=404
        )