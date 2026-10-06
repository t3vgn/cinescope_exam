import pytest

from tests.conftest import unauthorized_api
from utils.data_generator import DataGenerator


@pytest.mark.api
class TestMoviesPositive:

    def test_get_movies_list(self, api):
        response = api.movies.get_movies()
        assert response.status_code == 200
        data = response.json()
        assert "movies" in data
        assert isinstance(data["movies"], list)

    def test_get_movies_with_filter_min_price(self, authorized_api):
        cheap = authorized_api.movies.create_movie(
            DataGenerator.generate_movie_payload(price=100)
        ).json()
        middle = authorized_api.movies.create_movie(
            DataGenerator.generate_movie_payload(price=700)
        ).json()
        expensive = authorized_api.movies.create_movie(
            DataGenerator.generate_movie_payload(price=1500)
        ).json()
        params = {
            "page": 1,
            "pageSize": 20,
            "minPrice": 500,
            "maxPrice": 1000,
            "createdAt": "desc",
        }
        response = authorized_api.movies.get_movies(params=params)
        assert response.status_code == 200

        movies = response.json()["movies"]
        assert movies, "Список фильмов пустой"

        ids = [movie["id"] for movie in movies]
        assert middle["id"] in ids, "Фильм за 700₽ должен попасть в фильтр"
        assert cheap["id"] not in ids, "Фильм за 100₽ не должен попасть"
        assert expensive["id"] not in ids, "Фильм за 1500₽ не должен попасть"

        for movie in movies:
            assert 500 <= movie["price"] <= 1000

        for m in [cheap, middle, expensive]:
            authorized_api.movies.delete_movie(m["id"])

    def test_get_movies_with_filter_location(self, authorized_api):
        msk_movie = authorized_api.movies.create_movie(
            DataGenerator.generate_movie_payload(location="MSK")
        ).json()
        spb_movie = authorized_api.movies.create_movie(
            DataGenerator.generate_movie_payload(location="SPB")
        ).json()


        params = {
            "page": 1,
            "pageSize": 20,
            "locations": ["MSK"],
            "createdAt": "desc",
        }
        response = authorized_api.movies.get_movies(params=params)
        assert response.status_code == 200

        movies = response.json()["movies"]
        assert movies, "Список фильмов пустой"

        ids = [movie["id"] for movie in movies]


        assert msk_movie["id"] in ids, "Фильм MSK должен быть в ответе"
        assert spb_movie["id"] not in ids, "Фильм SPB не должен быть в ответе"


        for movie in movies:
            assert movie["location"] == "MSK"


        authorized_api.movies.delete_movie(msk_movie["id"])
        authorized_api.movies.delete_movie(spb_movie["id"])

    def test_get_movie_by_id(self, authorized_api, created_movie):
        response = authorized_api.movies.get_movie_by_id(created_movie["id"])
        assert response.status_code == 200
        assert response.json()["id"] == created_movie["id"]

    def test_create_movie(self, authorized_api):

        movie_data = DataGenerator.generate_movie_payload()
        response = authorized_api.movies.create_movie(movie_data)

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == movie_data["name"]

        movie_id = body["id"]
        get_response = authorized_api.movies.get_movie_by_id(movie_id)
        assert get_response.status_code == 200

        actual = get_response.json()
        assert actual["name"] == movie_data["name"], \
            "Имя не совпадает после создания"
        assert actual["price"] == movie_data["price"], \
            "Цена не совпадает после создания"
        assert actual["location"] == movie_data["location"], \
            "Локация не совпадает после создания"

        # Cleanup
        authorized_api.movies.delete_movie(movie_id)

    def test_patch_movie(self, authorized_api, created_movie):
        patch_data = DataGenerator.generate_movie_patch_data()
        response = authorized_api.movies.patch_movie(
            created_movie["id"], patch_data
        )

        assert response.status_code == 200
        assert response.json()["name"] == patch_data["name"]

        get_response = authorized_api.movies.get_movie_by_id(created_movie["id"])
        assert get_response.status_code == 200

        actual = get_response.json()
        assert actual["name"] == patch_data["name"], \
            "Имя не сохранилось после PATCH"
        assert actual["price"] == patch_data["price"], \
            "Цена не сохранилась после PATCH"

    def test_delete_movie(self, authorized_api):
        movie_data = DataGenerator.generate_movie_payload()
        created = authorized_api.movies.create_movie(movie_data).json()

        response = authorized_api.movies.delete_movie(created["id"])
        assert response.status_code == 200

        authorized_api.movies.send_request(
            "GET", f"/movies/{created['id']}", expected_status=404
        )


@pytest.mark.api
class TestMoviesNegative:

    def test_get_movie_by_nonexistent_id(self, api):
        api.movies.send_request(
            "GET", "/movies/99999999", expected_status=404
        )

    def test_create_movie_without_auth(self, unauthorized_api):
        movie_data = DataGenerator.generate_movie_payload()
        response = unauthorized_api.movies.send_request(
            "POST", "/movies", data=movie_data, expected_status=401
        )
        assert response.status_code == 401

    def test_create_movie_without_required_field(self, authorized_api):
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

    def test_delete_movie_without_auth(self, api, unauthorized_api, created_movie):
        response = unauthorized_api.movies.send_request(
            "DELETE", f"/movies/{created_movie['id']}",
            expected_status=401
        )
        assert response.status_code == 401

    def test_patch_nonexistent_movie(self, authorized_api):
        patch_data = DataGenerator.generate_movie_patch_data()
        authorized_api.movies.send_request(
            "PATCH", "/movies/99999999",
            data=patch_data, expected_status=404
        )