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
from app.schemas import DashboardSummary, LessonStats
from app.services.stats import lesson_stats
from app.utils import duration_to_minutes, minutes_to_hours

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def summary(
    student_repo: StudentRepository = Depends(get_student_repo),
    coach_repo: CoachRepository = Depends(get_coach_repo),
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    cancel_rule_repo: CancelRuleRepository = Depends(get_cancel_rule_repo),
) -> DashboardSummary:
    completed_appointments = appointment_repo.list_by_status(AppointmentStatus.completed)
    completed_minutes = sum(
        duration_to_minutes(item.start_time, item.end_time)
        for item in completed_appointments
    )
    booked_appointments = appointment_repo.list_by_status(AppointmentStatus.booked)
    return DashboardSummary(
        total_students=len(student_repo.list_all()),
        total_coaches=len(coach_repo.list_all()),
        active_bookings=len(booked_appointments),
        completed_hours=minutes_to_hours(completed_minutes),
        cancel_rule=cancel_rule_repo.get().model_dump(),
    )


@router.get("/lesson-stats", response_model=list[LessonStats])
def get_lesson_stats(
    student_repo: StudentRepository = Depends(get_student_repo),
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
) -> list[LessonStats]:
    return lesson_stats(student_repo, appointment_repo)
