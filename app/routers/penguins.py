"""All /penguins endpoints. NOTE: /random and /daily are declared BEFORE /{species_id},
otherwise FastAPI would treat the words "random"/"daily" as species IDs."""
import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.database import get_session
from app.models import Penguin, PenguinFact

router = APIRouter(prefix="/penguins", tags=["penguins"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[schemas.PenguinSummary], summary="List all penguin species")
async def list_penguins(
    session: SessionDep,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result = await session.scalars(
        select(Penguin).order_by(Penguin.common_name).limit(limit).offset(offset)
    )
    return result.all()


@router.get("/random", response_model=schemas.FactCard, summary="Random penguin fact + image")
async def random_fact(session: SessionDep):
    fact = await session.scalar(select(PenguinFact).order_by(func.random()).limit(1))
    if fact is None:
        raise HTTPException(404, "No facts available")
    return schemas.FactCard(
        fact=schemas.PenguinFact.model_validate(fact),
        penguin=schemas.PenguinSummary.model_validate(fact.penguin),
    )


@router.get("/daily", response_model=schemas.DailyPenguin, summary="Penguin of the Day (UTC date)")
async def daily(
    session: SessionDep,
    on: dt.date | None = Query(None, description="Override the date (YYYY-MM-DD), handy for testing"),
):
    # Deterministic: same date -> same penguin, for every caller, with no state stored.
    day = on or dt.datetime.now(dt.timezone.utc).date()
    ordinal = day.toordinal()

    ids = (await session.scalars(select(Penguin.id).order_by(Penguin.id))).all()
    if not ids:
        raise HTTPException(404, "No penguins available")

    penguin = await session.get(Penguin, ids[ordinal % len(ids)])
    facts = sorted(penguin.facts, key=lambda f: f.id)
    # Rotate facts once every species has had a turn, so repeats feel fresh.
    fact = facts[(ordinal // len(ids)) % len(facts)] if facts else None

    return schemas.DailyPenguin(
        date=day,
        penguin=schemas.Penguin.model_validate(penguin),
        fact=schemas.PenguinFact.model_validate(fact) if fact else None,
    )


@router.get("/{species_id}", response_model=schemas.Penguin, summary="Detailed species data")
async def get_penguin(
    session: SessionDep,
    species_id: Annotated[str, Path(pattern=r"^[a-z0-9-]{1,64}$", examples=["emperor"])],
):
    penguin = await session.get(Penguin, species_id)
    if penguin is None:
        raise HTTPException(404, f"Species '{species_id}' not found")
    return penguin
