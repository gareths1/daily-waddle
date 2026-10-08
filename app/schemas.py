"""Pydantic response models (the public API contract)."""
import datetime as dt

from pydantic import BaseModel, ConfigDict


class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PenguinFact(_ORM):
    id: int
    text: str
    source: str | None = None


class PenguinSummary(_ORM):
    id: str
    common_name: str
    scientific_name: str
    conservation_status: str
    image_url: str


class Penguin(PenguinSummary):
    height_cm: float
    weight_kg: float
    diet: str
    habitat: str
    facts: list[PenguinFact] = []


class FactCard(BaseModel):
    """Returned by /random: one fact plus the penguin it belongs to."""
    fact: PenguinFact
    penguin: PenguinSummary


class DailyPenguin(BaseModel):
    """Returned by /daily: the Penguin of the Day plus a featured fact."""
    date: dt.date
    penguin: Penguin
    fact: PenguinFact | None
