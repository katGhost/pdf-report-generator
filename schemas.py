from pydantic import BaseModel, ConfigDict, HttpUrl

class BookCreate(BaseModel):
    title: str
    url: HttpUrl | str
    price: int
    rating: int


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    url: HttpUrl | str
    price: int
    rating: int
    