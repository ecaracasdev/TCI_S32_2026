from pydantic import BaseModel


class ProductDto(BaseModel):
    id: int
    sku: str
    name: str