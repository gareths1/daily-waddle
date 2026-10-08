"""SQLAlchemy ORM models (database schema)."""
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Penguin(Base):
    __tablename__ = "penguins"

    # Human-friendly slug as primary key, e.g. "emperor", "little-blue"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    common_name: Mapped[str] = mapped_column(String(100), index=True)
    scientific_name: Mapped[str] = mapped_column(String(100))
    height_cm: Mapped[float]          # typical adult standing height
    weight_kg: Mapped[float]          # typical adult weight
    conservation_status: Mapped[str] = mapped_column(String(40))  # IUCN category
    diet: Mapped[str] = mapped_column(Text)
    habitat: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String(500))

    facts: Mapped[list["PenguinFact"]] = relationship(
        back_populates="penguin", lazy="selectin", cascade="all, delete-orphan"
    )


class PenguinFact(Base):
    __tablename__ = "penguin_facts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    penguin_id: Mapped[str] = mapped_column(ForeignKey("penguins.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(300), default=None)

    penguin: Mapped[Penguin] = relationship(back_populates="facts", lazy="joined")
