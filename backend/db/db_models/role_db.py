from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class RoleDb(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rolename: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    users: Mapped[list["UserDb"]] = relationship(
        secondary="role_x_user_db",
        back_populates="roles",
        lazy="selectin",
        overlaps="user,role",
    )
