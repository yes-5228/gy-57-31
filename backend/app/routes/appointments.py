from fastapi import APIRouter, Depends

from app.dependencies import (
    get_appointment_repo,
    get_cancel_rule_repo,
    get_coach_repo,
    get_student_repo,
)
from app.models import AppointmentStatus
from app.repositories.base import (
    AppointmentRepository,
    CancelRuleRepository,
    CoachRepository,
    StudentRepository,
)
from app.schemas import AppointmentCancel, AppointmentCreate, AppointmentRead
from app.services.appointments import cancel_appointment, create_appointment, list_appointments

router = APIRouter()


@router.get("", response_model=list[AppointmentRead])
def get_appointments(
    status: AppointmentStatus | None = None,
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    student_repo: StudentRepository = Depends(get_student_repo),
    coach_repo: CoachRepository = Depends(get_coach_repo),
) -> list[AppointmentRead]:
    return list_appointments(appointment_repo, student_repo, coach_repo, status)


@router.post("", response_model=AppointmentRead, status_code=201)
def book_appointment(
    payload: AppointmentCreate,
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    student_repo: StudentRepository = Depends(get_student_repo),
    coach_repo: CoachRepository = Depends(get_coach_repo),
    cancel_rule_repo: CancelRuleRepository = Depends(get_cancel_rule_repo),
) -> AppointmentRead:
    return create_appointment(
        payload,
        appointment_repo,
        student_repo,
        coach_repo,
        cancel_rule_repo,
    )


@router.post("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel(
    appointment_id: int,
    payload: AppointmentCancel,
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    student_repo: StudentRepository = Depends(get_student_repo),
    coach_repo: CoachRepository = Depends(get_coach_repo),
    cancel_rule_repo: CancelRuleRepository = Depends(get_cancel_rule_repo),
) -> AppointmentRead:
    return cancel_appointment(
        appointment_id,
        payload.reason,
        appointment_repo,
        student_repo,
        coach_repo,
        cancel_rule_repo,
    )
