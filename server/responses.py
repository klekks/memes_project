from pydantic import BaseModel, PositiveInt, Field, HttpUrl
from typing import Optional
from fastapi import Query
from settings import service_settings


class MemesInfo(BaseModel):
    id: PositiveInt
    text: str = Field(min_length=1, max_length=service_settings.MAX_MEMES_TEXT_LENGTH, description="Description of the "
                                                                                                   "meme. It will be "
                                                                                                   "attached to the "
                                                                                                   "image.")


class MemesFullInfo(MemesInfo):
    url: HttpUrl
