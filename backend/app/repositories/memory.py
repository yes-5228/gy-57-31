from datetime import datetime, timedelta

from app.models import Appointment, AppointmentStatus, CancelRule, Coach, Student
from app.repositories.base import (
    AppointmentRepository,
    CancelRuleRepository,
    CoachRepository,
    StudentRepository,
)


class MemoryStudentRepository(StudentRepository):
    def __init__(self) -> None:
        self._students: dict[int, Student] = {}
        self._next_id = 0

    def list_all(self) -> list[Student]:
        return list(self._students.values())

    def get_by_id(self, student_id: int) -> Student | None:
        return self._students.get(student_id)

    def add(self, student: Student) -> Student:
        self._students[student.id] = student
        return student

    def update_remaining_hours(self, student_id: int, hours: float) -> Student | None:
        student = self._students.get(student_id)
        if student:
            student.remaining_hours = hours
            self._students[student_id] = student
            return student
        return None

    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id


class MemoryCoachRepository(CoachRepository):
    def __init__(self) -> None:
        self._coaches: dict[int, Coach] = {}
        self._next_id = 0

    def list_all(self) -> list[Coach]:
        return list(self._coaches.values())

    def get_by_id(self, coach_id: int) -> Coach | None:
        return self._coaches.get(coach_id)

    def add(self, coach: Coach) -> Coach:
        self._coaches[coach.id] = coach
        return coach

    def update_active(self, coach_id: int, active: bool) -> Coach | None:
        coach = self._coaches.get(coach_id)
        if coach:
            coach.active = active
            self._coaches[coach_id] = coach
            return coach
        return None

    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id


class MemoryAppointmentRepository(AppointmentRepository):
    def __init__(self) -> None:
        self._appointments: dict[int, Appointment] = {}
        self._next_id = 0

    def list_all(self) -> list[Appointment]:
        return sorted(self._appointments.values(), key=lambda item: item.start_time)

    def list_by_status(self, status: AppointmentStatus) -> list[Appointment]:
        return [item for item in self.list_all() if item.status == status]

    def list_by_student(self, student_id: int) -> list[Appointment]:
        return [item for item in self.list_all() if item.student_id == student_id]

    def list_by_coach(self, coach_id: int) -> list[Appointment]:
        return [item for item in self.list_all() if item.coach_id == coach_id]

    def get_by_id(self, appointment_id: int) -> Appointment | None:
        return self._appointments.get(appointment_id)

    def add(self, appointment: Appointment) -> Appointment:
        self._appointments[appointment.id] = appointment
        return appointment

    def update(self, appointment: Appointment) -> Appointment | None:
        if appointment.id in self._appointments:
            self._appointments[appointment.id] = appointment
            return appointment
        return None

    def has_conflict(
        self,
        coach_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_id: int | None = None,
    ) -> bool:
        return any(
            item.status == AppointmentStatus.booked
            and item.coach_id == coach_id
            and item.id != exclude_id
            and start_time < item.end_time
            and end_time > item.start_time
            for item in self._appointments.values()
        )

    def count_active_by_student(self, student_id: int) -> int:
        return sum(
            1
            for item in self._appointments.values()
            if item.student_id == student_id and item.status == AppointmentStatus.booked
        )

    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id


class MemoryCancelRuleRepository(CancelRuleRepository):
    def __init__(self) -> None:
        self._rule = CancelRule()

    def get(self) -> CancelRule:
        return self._rule


def seed_demo_data(
    student_repo: MemoryStudentRepository,
    coach_repo: MemoryCoachRepository,
    appointment_repo: MemoryAppointmentRepository,
) -> None:
    if student_repo.list_all() or coach_repo.list_all() or appointment_repo.list_all():
        return

    s1 = Student(id=student_repo.next_id(), name="张小雨", phone="13800000001", remaining_hours=18)
    s2 = Student(id=student_repo.next_id(), name="李明", phone="13800000002", remaining_hours=12)
    student_repo.add(s1)
    student_repo.add(s2)

    c1 = Coach(
        id=coach_repo.next_id(),
        name="王教练",
        phone="13900000001",
        car_no="粤B-D1023",
        specialties=["科目二", "倒车入库"],
    )
    c2 = Coach(
        id=coach_repo.next_id(),
        name="陈教练",
        phone="13900000002",
        car_no="粤B-D2048",
        specialties=["科目三", "道路驾驶"],
    )
    coach_repo.add(c1)
    coach_repo.add(c2)

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    appt = Appointment(
        id=appointment_repo.next_id(),
        student_id=s1.id,
        coach_id=c1.id,
        start_time=now + timedelta(days=1, hours=1),
        end_time=now + timedelta(days=1, hours=3),
        status=AppointmentStatus.booked,
        created_at=now,
    )
    done = Appointment(
        id=appointment_repo.next_id(),
        student_id=s2.id,
        coach_id=c2.id,
        start_time=now - timedelta(days=1, hours=3),
        end_time=now - timedelta(days=1, hours=1),
        status=AppointmentStatus.completed,
        created_at=now - timedelta(days=2),
    )
    appointment_repo.add(appt)
    appointment_repo.add(done)
