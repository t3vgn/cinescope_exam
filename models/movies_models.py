from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class Location(str, Enum):
    MSK = "MSK"
    SPB = "SPB"


class GenreResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str


class MovieResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int
    name: str
    description: str
    image_url: Optional[str] = Field(..., alias="imageUrl")
    location: Location
    price: int
    rating: Optional[float] = Field(..., ge=0, le=10)
    genre_id: int = Field(..., alias="genreId")
    published: bool
    created_at: datetime = Field(..., alias="createdAt")
    genre: GenreResponse


class ReviewResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int
    rating: int = Field(..., ge=0, le=5)
    text: str
    created_at: datetime = Field(..., alias="createdAt")


class MovieDetails(MovieResponse):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    reviews: list[ReviewResponse] = []


class MoviesPage(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    movies: list[MovieResponse]
    page: int
    page_size: int = Field(..., alias="pageSize")
    page_count: int = Field(..., alias="pageCount")
    count: int


class MovieCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str
    price: int
    image_url: str = Field(..., alias="imageUrl")
    location: Location
    published: bool
    rating: Optional[float] = Field(None, ge=0, le=10)
    genre_id: int = Field(..., alias="genreId")


class MoviePatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = Field(None, alias="imageUrl")
    location: Optional[Location] = None
    published: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=10)
    genre_id: Optional[int] = Field(None, alias="genreId")