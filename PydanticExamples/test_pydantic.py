import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class User(BaseModel):
    name: str
    age: int
    adult: bool

def get_user():
    return {
        "name": "Alice",
        "age": 25,
        "adult": "true"
    }

def test_user_data():
    user = User(**get_user())
    assert user.name == "Alice"
    logger.info(f"{user.name=} {user.age=} {user.adult=}")