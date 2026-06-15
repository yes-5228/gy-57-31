from fastapi import APIRouter, Depends

from app.dependencies import get_student_repo
from app.models import Student
from app.repositories.base import StudentRepository
from app.schemas import StudentCreate, StudentRead
from app.utils import minutes_to_hours

router = APIRouter()


def _student_to_read(student: Student) -> StudentRead:
    return StudentRead(
        id=student.id,
        name=student.name,
        phone=student.phone,
        remaining_hours=minutes_to_hours(student.remaining_minutes),
    )


@router.get("", response_model=list[StudentRead])
def list_students(
    student_repo: StudentRepository = Depends(get_student_repo),
) -> list[StudentRead]:
    return [_student_to_read(s) for s in student_repo.list_all()]


@router.post("", response_model=StudentRead, status_code=201)
def create_student(
    payload: StudentCreate,
    student_repo: StudentRepository = Depends(get_student_repo),
) -> StudentRead:
    minutes = round(payload.remaining_hours * 60)
    student = Student(
        id=student_repo.next_id(),
        name=payload.name,
        phone=payload.phone,
        remaining_minutes=minutes,
    )
    student_repo.add(student)
    return _student_to_read(student)
