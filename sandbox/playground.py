import sys

from pydantic import ConfigDict, ValidationError
from sandbox import payloads
from sandbox.models import Movie, MovieDetails, MoviesPage

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def title(text):
    print(f"\n{'=' * 15} {text} {'=' * 15}")

title("1. Один вызов разбирает всё дерево")
page = MoviesPage(**payloads.MOVIES_PAGE)

print("тип page.movies         :", type(page.movies).__name__)
print("тип page.movies[0]      :", type(page.movies[0]).__name__)
print("тип page.movies[0].genre:", type(page.movies[0].genre).__name__)
print("доступ через точку      :", page.movies[0].genre.name)

title("2. Три уровня вложенности")
details = MovieDetails(**payloads.MOVIE_DETAILS)

print("фильм               :", details.name)
print("жанр (уровень 2)    :", details.genre.name)
print("автор отзыва (ур. 3):", details.reviews[0].user.fullName)
print("createdAt стал      :", type(details.createdAt).__name__)
print("location стал       :", repr(details.location))

title("3. Ошибка внутри вложенной модели")
try:
    MoviesPage(**payloads.BROKEN_TYPES)
except ValidationError as e:
    print(e)
    print("\nloc-кортежи:")
    for err in e.errors():
        print("   ", err["loc"], "->", err["type"])

title("4. Поломка на третьем уровне")
try:
    MovieDetails(**payloads.BROKEN_DEEP)
except ValidationError as e:
    for err in e.errors():
        print("   ", ".".join(str(p) for p in err["loc"]), "->", err["msg"])

title("5. Пропала вложенная модель")
try:
    MoviesPage(**payloads.MISSING_NESTED)
except ValidationError as e:
    for err in e.errors():
        print("   ", err["loc"], "->", err["msg"])

title("Задание 1: жанр второго фильма")
page = MoviesPage(**payloads.MOVIES_PAGE)
print("Жанр второго фильма:", page.movies[1].genre.name)

title("Задание 2: id у Genre = None")
page = MoviesPage(**payloads.MOVIES_PAGE)
print("id первого жанра:", page.movies[0].genre.id)
print("id второго жанра:", page.movies[1].genre.id)

title("Задание 4: reviews.0.user.fullName -> Field required")
broken = {**payloads.MOVIE_DETAILS}
broken["reviews"] = [
    {"rating": 5, "user": {"email": "m@mail.ru"}}   # ← нет fullName
]
try:
    MovieDetails(**broken)
except ValidationError as e:
    for err in e.errors():
        path = ".".join(str(p) for p in err["loc"])
        print(f"   {path} -> {err['msg']}")


title("6. extra: что делать с лишними полями")

print("-- ignore (по умолчанию) --")
p_ignore = MoviesPage(**payloads.WITH_EXTRA_FIELDS)
print("   объект создался, totalRevenue доступен?", hasattr(p_ignore, "totalRevenue"))

class MoviesPageAllow(MoviesPage):
    model_config = ConfigDict(extra="allow")

print("-- allow --")
p_allow = MoviesPageAllow(**payloads.WITH_EXTRA_FIELDS)
print("   model_extra          :", p_allow.model_extra)
print("   доступ .totalRevenue :", p_allow.totalRevenue)

class MoviesPageForbid(MoviesPage):
    model_config = ConfigDict(extra="forbid")

print("-- forbid --")
try:
    MoviesPageForbid(**payloads.WITH_EXTRA_FIELDS)
except ValidationError as e:
    for err in e.errors():
        print("   ", err["loc"], "->", err["msg"])


title("7. strict: запрещаем приведение типов")

class StrictMovie(Movie):
    model_config = ConfigDict(strict=True)

sample = dict(payloads.MOVIES_PAGE["movies"][0])
sample["price"] = "130"          # цена пришла строкой

print("-- lax --")
print("   price ->", Movie(**sample).price, type(Movie(**sample).price).__name__)

print("-- strict --")
try:
    StrictMovie(**sample)
except ValidationError as e:
    for err in e.errors():
        print("   ", err["loc"], "->", err["msg"])

print("-- EXTRA --")
try:
    MoviesPageForbid(**payloads.WITH_EXTRA_FIELDS)
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], "->", err["msg"])