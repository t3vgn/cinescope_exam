# db_requester/db_client.py
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from resources.db_creds import get_db_creds

logger = logging.getLogger(__name__)


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
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        return self.Session()
    
    def close(self):
        self.engine.dispose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
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


_db_client_instance = None


def get_db_client() -> DBClient:
    global _db_client_instance
    if _db_client_instance is None:
        _db_client_instance = DBClient()
    return _db_client_instance


def get_db_session() -> Session:
    return get_db_client().get_session()