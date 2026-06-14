from datetime import datetime

from fastapi import HTTPException, status

from app.models import Appointment, AppointmentStatus
from app.repositories.base import (
    AppointmentRepository,
    CancelRuleRepository,
    CoachRepository,
    StudentRepository,
)
from app.schemas import AppointmentCreate, AppointmentRead


def appointment_to_read(
    appointment: Appointment,
    student_repo: StudentRepository,
    coach_repo: CoachRepository,
) -> AppointmentRead:
    student = student_repo.get_by_id(appointment.student_id)
    coach = coach_repo.get_by_id(appointment.coach_id)
    return AppointmentRead(
        id=appointment.id,
        student_id=student.id,
        student_name=student.name,
        coach_id=coach.id,
        coach_name=coach.name,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        status=appointment.status,
        created_at=appointment.created_at,
        cancelled_at=appointment.cancelled_at,
        cancel_reason=appointment.cancel_reason,
    )


def list_appointments(
    appointment_repo: AppointmentRepository,
    student_repo: StudentRepository,
    coach_repo: CoachRepository,
    status_filter: AppointmentStatus | None = None,
) -> list[AppointmentRead]:
    if status_filter:
        values = appointment_repo.list_by_status(status_filter)
    else:
        values = appointment_repo.list_all()
    return [appointment_to_read(item, student_repo, coach_repo) for item in values]


def create_appointment(
    payload: AppointmentCreate,
    appointment_repo: AppointmentRepository,
    student_repo: StudentRepository,
    coach_repo: CoachRepository,
    cancel_rule_repo: CancelRuleRepository,
) -> AppointmentRead:
    student = student_repo.get_by_id(payload.student_id)
    if not student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")

    coach = coach_repo.get_by_id(payload.coach_id)
    if not coach or not coach.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Active coach not found")

    start_time = _as_naive(payload.start_time)
    end_time = _as_naive(payload.end_time)

    if start_time <= datetime.now():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot book a past time slot")

    cancel_rule = cancel_rule_repo.get()
    active_count = appointment_repo.count_active_by_student(payload.student_id)
    if active_count >= cancel_rule.max_active_bookings_per_student:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Student has reached active booking limit")

    if appointment_repo.has_conflict(payload.coach_id, start_time, end_time):
        raise HTTPException(status.HTTP_409_CONFLICT, "Coach already has a booking in this time slot")

    duration_hours = (end_time - start_time).total_seconds() / 3600
    if student.remaining_hours < duration_hours:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Student does not have enough remaining hours")

    appointment = Appointment(
        id=appointment_repo.next_id(),
        student_id=payload.student_id,
        coach_id=payload.coach_id,
        start_time=start_time,
        end_time=end_time,
        created_at=datetime.now(),
    )
    appointment_repo.add(appointment)

    student_repo.update_remaining_hours(
        payload.student_id,
        student.remaining_hours - int(duration_hours),
    )

    return appointment_to_read(appointment, student_repo, coach_repo)


def _as_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone().replace(tzinfo=None)


def cancel_appointment(
    appointment_id: int,
    reason: str,
    appointment_repo: AppointmentRepository,
    student_repo: StudentRepository,
    coach_repo: CoachRepository,
    cancel_rule_repo: CancelRuleRepository,
) -> AppointmentRead:
    appointment = appointment_repo.get_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
    if appointment.status == AppointmentStatus.cancelled:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Appointment already cancelled")

    cancel_rule = cancel_rule_repo.get()
    if appointment.status == AppointmentStatus.completed and not cancel_rule.allow_cancel_completed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Completed appointments cannot be cancelled")

    hours_before_start = (appointment.start_time - datetime.now()).total_seconds() / 3600
    if hours_before_start < cancel_rule.min_hours_before_start:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Appointments must be cancelled at least {cancel_rule.min_hours_before_start} hours in advance",
        )

    appointment.status = AppointmentStatus.cancelled
    appointment.cancelled_at = datetime.now()
    appointment.cancel_reason = reason
    appointment_repo.update(appointment)

    return appointment_to_read(appointment, student_repo, coach_repo)
