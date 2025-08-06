from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, Enum as SqlEnum
from app.schemas.user import RoleEnum

Base = declarative_base(cls=AsyncAttrs)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum), nullable=False, default=RoleEnum.enduser)
