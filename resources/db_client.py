from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from resources.db_creds import get_db_creds       # ← импорт функции

_creds = get_db_creds()

engine = create_engine(
    f"postgresql+psycopg2://{_creds.user}:{_creds.password}"
    f"@{_creds.host}:{_creds.port}/{_creds.dbname}",
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    return SessionLocal()