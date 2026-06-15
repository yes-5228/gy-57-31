from app.models import AppointmentStatus
from app.repositories.base import AppointmentRepository, StudentRepository
from app.schemas import LessonStats
from app.utils import duration_to_minutes, minutes_to_hours


def lesson_stats(
    student_repo: StudentRepository,
    appointment_repo: AppointmentRepository,
) -> list[LessonStats]:
    result: list[LessonStats] = []
    students = student_repo.list_all()
    for student in students:
        student_appointments = appointment_repo.list_by_student(student.id)
        completed_minutes = sum(
            duration_to_minutes(item.start_time, item.end_time)
            for item in student_appointments
            if item.status == AppointmentStatus.completed
        )
        booked_minutes = sum(
            duration_to_minutes(item.start_time, item.end_time)
            for item in student_appointments
            if item.status == AppointmentStatus.booked
        )
        cancelled_count = sum(1 for item in student_appointments if item.status == AppointmentStatus.cancelled)
        result.append(
            LessonStats(
                student_id=student.id,
                student_name=student.name,
                completed_hours=minutes_to_hours(completed_minutes),
                booked_hours=minutes_to_hours(booked_minutes),
                cancelled_count=cancelled_count,
                remaining_hours=minutes_to_hours(student.remaining_minutes),
            )
        )
    return result
