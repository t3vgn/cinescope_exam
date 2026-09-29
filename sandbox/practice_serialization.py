from enum import Enum
from pydantic import BaseModel

class Roles(str, Enum):
    USER = "user"
    ADMIN = "admin"

class TestUser(BaseModel):
    email: str
    full_name: str
    password: str
    roles: list[Roles] = [Roles.USER]
    verified: bool = False
    banned: bool = False

user = TestUser(
    email="test@example.com",
    full_name="Test User",
    password="qwerty123",
)

print(user.model_dump_json())
print(user.model_dump_json(exclude_unset=True))
print(user.model_dump_json(exclude_none=True))

