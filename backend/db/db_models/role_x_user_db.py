from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class RoleXUserDb(Base):
    __tablename__ = "role_x_user_db"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)

    user: Mapped["UserDb"] = relationship(overlaps="roles,users")
    role: Mapped["RoleDb"] = relationship(overlaps="roles,users")
