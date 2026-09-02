from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_db import Base

class ProductDb(Base):
    __tablename__ = "products"
    id: Mapped[int] =                  mapped_column(Integer, primary_key=True)
    sku: Mapped[str] =    mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] =              mapped_column(String(200), nullable=False)
