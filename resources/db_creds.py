import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class DBCreds:
    host: str
    port: int
    dbname: str
    user: str
    password: str


def get_db_creds() -> DBCreds:
    return DBCreds(
        host=os.environ["DB_MOVIES_HOST"],
        port=int(os.environ["DB_MOVIES_PORT"]),
        dbname=os.environ["DB_MOVIES_NAME"],
        user=os.environ["DB_MOVIES_USERNAME"],
        password=os.environ["DB_MOVIES_PASSWORD"],
    )