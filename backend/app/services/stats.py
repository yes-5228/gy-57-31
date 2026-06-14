from app.models import AppointmentStatus
from app.repositories.base import AppointmentRepository, StudentRepository
from app.schemas import LessonStats


def _hours(start, end) -> float:
    return round((end - start).total_seconds() / 3600, 1)


def lesson_stats(
    student_repo: StudentRepository,
    appointment_repo: AppointmentRepository,
) -> list[LessonStats]:
    result: list[LessonStats] = []
    students = student_repo.list_all()
    for student in students:
        student_appointments = appointment_repo.list_by_student(student.id)
        completed_hours = sum(
            _hours(item.start_time, item.end_time)
            for item in student_appointments
            if item.status == AppointmentStatus.completed
        )
        booked_hours = sum(
            _hours(item.start_time, item.end_time)
            for item in student_appointments
            if item.status == AppointmentStatus.booked
        )
        cancelled_count = sum(1 for item in student_appointments if item.status == AppointmentStatus.cancelled)
        result.append(
            LessonStats(
                student_id=student.id,
                student_name=student.name,
                completed_hours=round(completed_hours, 1),
                booked_hours=round(booked_hours, 1),
                cancelled_count=cancelled_count,
                remaining_hours=student.remaining_hours,
            )
        )
    return result
