from dataclasses import dataclass
from pydantic import BaseModel, Field,field_validator, ValidationInfo
from pydantic_core.core_schema import ValidationInfo

from clients.api_manager import ApiManager

@dataclass
class Credentials:
    email: str
    password: str

class User:
    def __init__(self, email, password, roles, session):
        self.email = email
        self.password = password
        self.roles = roles
        self.session = session
        self.api = ApiManager(session=session)

    @property
    def creds(self):
        return Credentials(email=self.email, password=self.password)