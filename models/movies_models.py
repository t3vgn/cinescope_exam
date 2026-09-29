from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MovieResponse(BaseModel):

    model_config = ConfigDict(extra="ignore", populate_by_name=True,)

    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, alias="imageUrl")
    location: Optional[str] = None
    price: int
    rating: Optional[float] = None
    genre_id: Optional[int] = Field(None, alias="genreId")
    published: Optional[bool] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class MoviesPage(BaseModel):

    model_config = ConfigDict(extra="ignore")

    page: int
    page_size: int = Field(..., alias="pageSize")
    page_count: int = Field(..., alias="pageCount")
    movies: list[MovieResponse]


class MovieCreateRequest(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str
    price: int
    image_url: str = Field(..., alias="imageUrl")
    location: str
    published: bool
    rating: Optional[float] = None
    genre_id: int = Field(..., alias="genreId")


class MoviePatchRequest(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = Field(None, alias="imageUrl")
    location: Optional[str] = None
    published: Optional[bool] = None
    rating: Optional[float] = None
    genre_id: Optional[int] = Field(None, alias="genreId")