import pytest
import allure
from models.movies_models import MovieDetails
from sqlalchemy.orm import Session
import logging

from models.movies_models import MoviesPage, MovieResponse, MovieCreateRequest, MoviePatchRequest
from utils.data_generator import DataGenerator
from db_models.movies import MovieDBModel

logger = logging.getLogger(__name__)


@allure.epic("Управление фильмами")
@allure.feature("Позитивные сценарии работы с фильмами")
@pytest.mark.api
class TestMoviesPositive:

    # SMOKE — критичные happy-path

    @allure.story("Получение списка фильмов")
    @allure.title("Получение списка фильмов под SUPER_ADMIN")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_movies_list(self, super_admin):
        with allure.step("Отправляем GET /movies под SUPER_ADMIN"):
            response = super_admin.api.movies.get_movies()

        with allure.step("Проверяем статус 200"):
            assert response.status_code == 200

        with allure.step("Валидируем ответ через MoviesPage (проверка контракта)"):
            page = MoviesPage.model_validate(response.json())

        with allure.step("Проверяем, что список фильмов непустой"):
            assert page.movies, "Список фильмов пустой"
            assert page.count >= len(page.movies), (
                f"Общее количество фильмов ({page.count}) "
                f"не может быть меньше размера страницы ({len(page.movies)})"
            )

    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма по ID через API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_get_movie_by_id(self, authorized_api, created_movie):
        movie_id = created_movie["id"]

        with allure.step(f"Запрашиваем фильм id={movie_id}"):
            response = authorized_api.movies.get_movie_by_id(movie_id)

        with allure.step("Проверяем статус 200"):
            assert response.status_code == 200, (
                f"Ожидали 200, получили {response.status_code}: {response.text}"
            )

        with allure.step("Валидируем ответ через MovieDetails (проверка контракта)"):
            movie = MovieDetails.model_validate(response.json())

        with allure.step("Проверяем, что id совпадает"):
            assert movie.id == movie_id, (
                f"Ожидали id={movie_id}, получили id={movie.id}"
            )

        with allure.step("Проверяем, что reviews — список"):
            assert isinstance(movie.reviews, list), (
                f"reviews должен быть списком, получили: {type(movie.reviews).__name__}"
            )

    @allure.story("Создание фильма")
    @allure.title("Создание фильма через API и проверка полей")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_movie(self, super_admin):
        with allure.step("Генерируем payload фильма и валидируем через MovieCreateRequest"):
            movie_data = DataGenerator.generate_movie_payload()
            payload = MovieCreateRequest.model_validate(movie_data)

        with allure.step("Создаём фильм через POST /movies"):
            response = super_admin.api.movies.create_movie(payload)

        with allure.step("Проверяем статус 201 и валидируем ответ"):
            assert response.status_code == 201
            created = MovieResponse.model_validate(response.json())
            assert created.name == payload.name

        with allure.step("Получаем фильм через GET и сверяем поля"):
            get_response = super_admin.api.movies.get_movie_by_id(created.id)
            assert get_response.status_code == 200

            actual = MovieResponse.model_validate(get_response.json())
            assert actual.name == payload.name, "Имя не совпадает"
            assert actual.price == payload.price, "Цена не совпадает"
            assert actual.location == payload.location, "Локация не совпадает"

        with allure.step("Cleanup: удаляем созданный фильм"):
            super_admin.api.movies.delete_movie(created.id)

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма через API с проверкой в БД")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_delete_movie(self, super_admin, db_session: Session):

        with allure.step("Создаём фильм через POST /movies"):
            movie_data = DataGenerator.generate_movie_payload()
            response = super_admin.api.movies.create_movie(movie_data)

        with allure.step("Проверяем статус 201 и валидируем ответ"):
            assert response.status_code == 201, (
                f"Ожидали 201, получили {response.status_code}: {response.text}"
            )
            created = MovieResponse.model_validate(response.json())
            movie_id = created.id

        with allure.step(f"Проверяем в БД, что фильм id={movie_id} существует"):
            db_session.expire_all()
            movie_in_db = (
                db_session.query(MovieDBModel)
                .filter(MovieDBModel.id == movie_id)
                .first()
            )
            assert movie_in_db is not None, (
                f"Фильм id={movie_id} должен существовать в БД после создания"
            )

        with allure.step(f"Удаляем фильм id={movie_id} через DELETE /movies/{movie_id}"):
            delete_response = super_admin.api.movies.delete_movie(movie_id)

        with allure.step("Проверяем статус 200"):
            assert delete_response.status_code == 200, (
                f"Ожидали 200, получили {delete_response.status_code}: "
                f"{delete_response.text}"
            )

        with allure.step(f"Проверяем в БД, что фильм id={movie_id} удалён"):
            db_session.expire_all()
            movie_in_db = (
                db_session.query(MovieDBModel)
                .filter(MovieDBModel.id == movie_id)
                .first()
            )
            assert movie_in_db is None, (
                f"Фильм id={movie_id} должен быть удалён из БД"
            )

    # REGRESSION — фильтры и PATCH

    @allure.story("Фильтрация фильмов")
    @allure.title("Фильтрация фильмов по диапазону цен 500–1000")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_get_movies_with_filter_min_price(self, authorized_api):
        with allure.step("Создаём фильмы 100₽ / 700₽ / 1500₽"):
            cheap = MovieResponse.model_validate(authorized_api.movies.create_movie(
                DataGenerator.generate_movie_payload(price=100)
            ).json())
            middle = MovieResponse.model_validate(authorized_api.movies.create_movie(
                DataGenerator.generate_movie_payload(price=700)
            ).json())
            expensive = MovieResponse.model_validate(authorized_api.movies.create_movie(
                DataGenerator.generate_movie_payload(price=1500)
            ).json())

        with allure.step("Запрашиваем фильмы с minPrice=500, maxPrice=1000"):
            params = {
                "page": 1, "pageSize": 20,
                "minPrice": 500, "maxPrice": 1000,
                "createdAt": "desc",
            }
            response = authorized_api.movies.get_movies(params=params)

        with allure.step("Проверяем статус и валидируем MoviesPage"):
            assert response.status_code == 200
            page = MoviesPage.model_validate(response.json())
            assert page.movies, "Список пустой"

        with allure.step("Проверяем, что попал только фильм за 700₽"):
            ids = [m.id for m in page.movies]
            assert middle.id in ids
            assert cheap.id not in ids
            assert expensive.id not in ids

        with allure.step("Все цены в диапазоне"):
            for movie in page.movies:
                assert 500 <= movie.price <= 1000

        with allure.step("Cleanup: удаляем фильмы"):
            for m in [cheap, middle, expensive]:
                authorized_api.movies.delete_movie(m.id)

    @allure.story("Фильтрация фильмов")
    @allure.title("Фильтрация фильмов по локации MSK")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_get_movies_with_filter_location(self, authorized_api):
        with allure.step("Создаём MSK и SPB фильмы"):
            msk_movie = MovieResponse.model_validate(authorized_api.movies.create_movie(
                DataGenerator.generate_movie_payload(location="MSK")
            ).json())
            spb_movie = MovieResponse.model_validate(authorized_api.movies.create_movie(
                DataGenerator.generate_movie_payload(location="SPB")
            ).json())

        with allure.step("Запрашиваем фильмы с locations=['MSK']"):
            params = {
                "page": 1, "pageSize": 20,
                "locations": ["MSK"], "createdAt": "desc",
            }
            response = authorized_api.movies.get_movies(params=params)

        with allure.step("Проверяем ответ и валидируем MoviesPage"):
            assert response.status_code == 200
            page = MoviesPage.model_validate(response.json())
            assert page.movies
            ids = [m.id for m in page.movies]
            assert msk_movie.id in ids
            assert spb_movie.id not in ids

        with allure.step("У всех фильмов location == 'MSK'"):
            for movie in page.movies:
                assert movie.location == "MSK"

        with allure.step("Cleanup"):
            authorized_api.movies.delete_movie(msk_movie.id)
            authorized_api.movies.delete_movie(spb_movie.id)

    @allure.story("Изменение фильма")
    @allure.title("Частичное обновление фильма через PATCH")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_patch_movie(self, authorized_api, created_movie):
        with allure.step("Генерируем данные для PATCH и валидируем"):
            patch_data = DataGenerator.generate_movie_patch_data()
            payload = MoviePatchRequest.model_validate(patch_data)

        with allure.step("Отправляем PATCH"):
            response = authorized_api.movies.patch_movie(
                created_movie["id"], payload)

        with allure.step("Проверяем статус 200 и валидируем ответ"):
            assert response.status_code == 200
            patched = MovieResponse.model_validate(response.json())
            assert patched.name == payload.name

        with allure.step("Проверяем сохранение через GET"):
            get_response = authorized_api.movies.get_movie_by_id(created_movie["id"])
            assert get_response.status_code == 200
            actual = MovieResponse.model_validate(get_response.json())
            assert actual.name == payload.name
            assert actual.price == payload.price

    @allure.story("Фильтрация фильмов")
    @allure.title("Параметризованный фильтр по цене")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("min_price, max_price", [
        (1, 100), (100, 500), (500, 1000), (1, 1000),
    ])
    def test_filter_by_price_range(self, api, min_price, max_price):
        with allure.step(f"Запрос с [{min_price}, {max_price}]"):
            params = {
                "page": 1, "pageSize": 10,
                "minPrice": min_price, "maxPrice": max_price,
            }
            response = api.movies.get_movies(params=params)

        with allure.step("Проверяем статус и валидируем MoviesPage"):
            assert response.status_code == 200
            page = MoviesPage.model_validate(response.json())
            assert len(page.movies) > 0

        with allure.step("Все цены в диапазоне"):
            for movie in page.movies:
                assert min_price <= movie.price <= max_price, (
                    f"Фильм '{movie.name}' имеет цену {movie.price}, "
                    f"что не входит в диапазон [{min_price}, {max_price}]"
                )

    @allure.story("Фильтрация фильмов")
    @allure.title("Параметризованный фильтр по локации")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("location", ["MSK", "SPB"])
    def test_filter_by_location(self, api, location):
        with allure.step(f"Запрос locations=['{location}']"):
            params = {"page": 1, "pageSize": 10, "locations": [location]}
            response = api.movies.get_movies(params=params)

        with allure.step("Проверяем статус и валидируем MoviesPage"):
            assert response.status_code == 200
            page = MoviesPage.model_validate(response.json())
            assert len(page.movies) > 0

        with allure.step("Все фильмы в нужной локации"):
            for movie in page.movies:
                assert movie.location == location, (
                    f"Фильм '{movie.name}' в локации {movie.location}, "
                    f"а ожидали {location}"
                )

    @allure.story("Фильтрация фильмов")
    @allure.title("Параметризованный фильтр по жанру")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("genre_id", [5, 7, 8, 9])
    def test_filter_by_genre(self, api, genre_id):
        with allure.step(f"Запрос genreId={genre_id}"):
            params = {"page": 1, "pageSize": 10, "genreId": genre_id}
            response = api.movies.get_movies(params=params)

        with allure.step("Проверяем статус и валидируем MoviesPage"):
            assert response.status_code == 200
            page = MoviesPage.model_validate(response.json())
            assert len(page.movies) > 0

        with allure.step("Все фильмы нужного жанра"):
            for movie in page.movies:
                assert movie.genre_id == genre_id, (
                    f"Фильм '{movie.name}' имеет genreId={movie.genre_id}, "
                    f"а ожидали {genre_id}"
                )

    @allure.story("Фильтрация фильмов")
    @allure.title("Комбинированный фильтр: локация + цена")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("location, min_price, max_price", [
        ("MSK", 1, 500),
        ("SPB", 100, 1000),
    ])
    def test_filter_by_multiple_params(self, api, location, min_price, max_price):
        with allure.step(f"Запрос: {location}, [{min_price}, {max_price}]"):
            params = {
                "page": 1, "pageSize": 10,
                "locations": [location],
                "minPrice": min_price, "maxPrice": max_price,
            }
            response = api.movies.get_movies(params=params)

        with allure.step("Проверяем статус и валидируем MoviesPage"):
            assert response.status_code == 200
            page = MoviesPage.model_validate(response.json())
            assert len(page.movies) > 0

        with allure.step("Оба условия выполнены"):
            for movie in page.movies:
                assert movie.location == location
                assert min_price <= movie.price <= max_price


# НЕГАТИВНЫЕ ТЕСТЫ

@allure.epic("Управление фильмами")
@allure.feature("Негативные сценарии работы с фильмами")
@pytest.mark.api
class TestMoviesNegative:

    @allure.story("Создание фильма без авторизации")
    @allure.title("Создание фильма без токена → 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_create_movie_without_auth(self, unauthorized_api):
        with allure.step("Генерируем валидный payload"):
            movie_data = DataGenerator.generate_movie_payload()

        with allure.step("Отправляем POST без токена"):
            response = unauthorized_api.movies.create_movie(movie_data, expected_status=401,)

        with allure.step("Проверяем статус 401"):
            assert response.status_code == 401

    @allure.story("Удаление фильма без авторизации")
    @allure.title("Удаление фильма без токена → 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_delete_movie_without_auth(self, api, unauthorized_api, created_movie):
        with allure.step("DELETE без токена"):
            response = unauthorized_api.movies.delete_movie(created_movie["id"], expected_status=401,)

        with allure.step("Проверяем статус 401"):
            assert response.status_code == 401

    @allure.story("Получение фильма по ID")
    @allure.title("Получение несуществующего фильма → 404")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_get_movie_by_nonexistent_id(self, api):
        with allure.step("GET /movies/99999999, ожидаем 404"):
            api.movies.get_movie_by_id(99999999, expected_status=404)

    @allure.story("Создание фильма без обязательного поля")
    @allure.title("Создание фильма без 'name' → 400")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_create_movie_without_required_field(self, authorized_api):
        with allure.step("Получаем валидный genre_id"):
            valid_genre_id = DataGenerator.get_valid_genre_id()

        with allure.step("Формируем Payload без 'name'"):
            invalid_data = {
                "price": 500,
                "description": "No name",
                "location": "MSK",
                "published": True,
                "genreId": valid_genre_id,
                "imageUrl": "https://example.com/img.png",
            }

        with allure.step("POST /movies, ожидаем 400"):
            response = authorized_api.movies.create_movie(invalid_data, expected_status=400,)
        with allure.step("Проверяем статус 400"):
            assert response.status_code == 400

        with allure.step("Проверяем, что ошибка именно про 'name'"):
            error_text = str(response.json()).lower()
            assert "name" in error_text, (
                f"Ожидали ошибку про поле 'name', получили: {response.json()}"
            )
    @allure.story("Изменение несуществующего фильма")
    @allure.title("PATCH несуществующего фильма → 404")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_patch_nonexistent_movie(self, authorized_api):
        with allure.step("Генерируем payload"):
            patch_data = DataGenerator.generate_movie_patch_data()

        with allure.step("PATCH /movies/99999999, ожидаем 404"):
            authorized_api.movies.patch_movie(99999999, patch_data, expected_status=404)

    @allure.story("Создание фильма обычным пользователем")
    @allure.title("Создание фильма под USER → 403")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_create_movie_by_common_user(self, common_user):
        with allure.step("POST /movies под USER"):
            response = common_user.api.movies.create_movie(DataGenerator.generate_movie_payload(),expected_status=403,)

        with allure.step("Проверяем статус 403"):
            assert response.status_code == 403


# РОЛЕВАЯ МОДЕЛЬ

@allure.epic("Управление фильмами")
@allure.feature("Ролевая модель доступа")
@pytest.mark.api
class TestMoviesDeleteRoles:
    """Тесты удаления фильмов с ролевой моделью."""

    @allure.story("Права на удаление фильма по ролям")
    @allure.title("Удаление фильма под разными ролями")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("user_fixture, role, expected_status", [
        ("super_admin","SUPER_ADMIN", 200),
        ("admin_user","ADMIN", 403),
        ("common_user","USER", 403),
    ])
    def test_delete_movie_by_role(
        self, request, movie_by_super_admin,user_fixture, role, expected_status
    ):
        allure.dynamic.title(
            f"Удаление фильма под ролью {role}, ожидаем {expected_status}"
        )

        movie_id = movie_by_super_admin.id

        with allure.step(f"Получаем пользователя: {user_fixture}"):
            user = request.getfixturevalue(user_fixture)

        with allure.step(f"DELETE /movies/{movie_id} под ролью {role}"):
            delete_response = user.api.movies.delete_movie(
                movie_id, expected_status=expected_status
            )

        with allure.step(f"Проверяем статус {expected_status}"):
            assert delete_response.status_code == expected_status

        if expected_status == 200:
            with allure.step("Фильм удалён — проверяем 404 через API"):
                user.api.movies.get_movie_by_id(movie_id, expected_status=404)
        else:
            with allure.step(f"Роль {role} — фильм на месте"):
                user.api.movies.get_movie_by_id(movie_id, expected_status=200)

