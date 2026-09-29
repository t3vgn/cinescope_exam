from sqlalchemy import (
    create_engine,
    Column,
    String,
    Boolean,
    DateTime,
    ARRAY,
    MetaData,
)
from sqlalchemy.orm import declarative_base, sessionmaker

host = "80.90.191.123"
port = 31200
database_name = "db_movies"
username = "postgres"
password = "AmwFrtnR2"

connection_string = (
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}"
)
engine = create_engine(connection_string)


def sdl_alchemy_ORM():
    Base = declarative_base(metadata=MetaData(schema="public"))

    class User(Base):
        __tablename__ = "users"

        id = Column(String, primary_key=True)
        email = Column(String)
        full_name = Column(String)
        password = Column("password", String)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
        verified = Column(Boolean)
        banned = Column(Boolean)
        roles = Column(ARRAY(String))

    Session = sessionmaker(bind=engine)
    session = Session()

    user_id = "ed4b61a6-6b46-47a0-a79d-5e8809a1da90"

    user = session.query(User).filter(User.id == user_id).first()

    if user:
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Full Name: {user.full_name}")
        print(f"Password: {user.password}")
        print(f"Created At: {user.created_at}")
        print(f"Updated At: {user.updated_at}")
        print(f"Verified: {user.verified}")
        print(f"Banned: {user.banned}")
        print(f"Roles: {user.roles}")
    else:
        print("Пользователь не найден.")

    session.close()


if __name__ == "__main__":
    sdl_alchemy_ORM()