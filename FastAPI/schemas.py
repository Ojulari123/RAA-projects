from enum import Enum
from pydantic import BaseModel
from datetime import date

class GenreChoices(Enum):#Im guessing its the same thing as BaseModel, after research i would say similar not same
    ROCK = "rock"
    ELECTORNIC = "electronic"
    METAL = "metal"
    HIP_HOP = "hip-hop"

class Album(BaseModel):
    title: str
    release_date: date

class BandBase(BaseModel):
    name: str
    genre: str
    albums: list[Album] = []

class BandCreate(BandBase):
    pass

class BandwithID(BandBase):
    id: int