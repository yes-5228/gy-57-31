from fastapi import APIRouter, Depends

from app.dependencies import get_student_repo
from app.models import Student
from app.repositories.base import StudentRepository
from app.schemas import StudentCreate, StudentRead

router = APIRouter()


@router.get("", response_model=list[StudentRead])
def list_students(
    student_repo: StudentRepository = Depends(get_student_repo),
) -> list[Student]:
    return student_repo.list_all()


@router.post("", response_model=StudentRead, status_code=201)
def create_student(
    payload: StudentCreate,
    student_repo: StudentRepository = Depends(get_student_repo),
) -> Student:
    student = Student(id=student_repo.next_id(), **payload.model_dump())
    student_repo.add(student)
    return student
