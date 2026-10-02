from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from resources.db_creds import get_db_creds


class DBClient:
    def __init__(self):
        creds = get_db_creds()
        self._connection_string = (
            f"postgresql+psycopg2://{creds.user}:{creds.password}"
            f"@{creds.host}:{creds.port}/{creds.dbname}"
        )
        self.engine = create_engine(
            self._connection_string,
            echo=False,
            pool_pre_ping=True,
        )
        self.Session = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    def get_session(self) -> Session:
        return self.Session()

    def close(self) -> None:
        self.engine.dispose()

    def __enter__(self) -> "DBClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def get_server_info(self) -> dict:
        with self.engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            params = self.engine.url
            return {
                "version": version,
                "host": params.host,
                "port": params.port,
                "dbname": params.database,
                "user": params.username,
            }


_db_client_instance: DBClient | None = None


def get_db_client() -> DBClient:
    """Общий DBClient. Создаётся при первом вызове, живёт до конца процесса."""
    global _db_client_instance
    if _db_client_instance is None:
        _db_client_instance = DBClient()
    assert _db_client_instance is not None
    return _db_client_instance


def get_db_session() -> Session:
    return get_db_client().get_session()