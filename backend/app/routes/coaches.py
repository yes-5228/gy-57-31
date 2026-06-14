from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_coach_repo
from app.models import Coach
from app.repositories.base import CoachRepository
from app.schemas import CoachCreate, CoachRead

router = APIRouter()


@router.get("", response_model=list[CoachRead])
def list_coaches(
    active: bool | None = None,
    coach_repo: CoachRepository = Depends(get_coach_repo),
) -> list[Coach]:
    values = coach_repo.list_all()
    if active is not None:
        values = [coach for coach in values if coach.active == active]
    return values


@router.post("", response_model=CoachRead, status_code=201)
def create_coach(
    payload: CoachCreate,
    coach_repo: CoachRepository = Depends(get_coach_repo),
) -> Coach:
    coach = Coach(id=coach_repo.next_id(), **payload.model_dump())
    coach_repo.add(coach)
    return coach


@router.patch("/{coach_id}/active", response_model=CoachRead)
def update_coach_active(
    coach_id: int,
    active: bool,
    coach_repo: CoachRepository = Depends(get_coach_repo),
) -> Coach:
    coach = coach_repo.update_active(coach_id, active)
    if not coach:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Coach not found")
    return coach
