from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MovieDBModel(Base):

    __tablename__ = "movies"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer)
    rating = Column(Float)
    genre_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, name={self.name!r})>"