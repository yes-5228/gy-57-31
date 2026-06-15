from abc import ABC, abstractmethod
from datetime import datetime

from app.models import Appointment, AppointmentStatus, CancelRule, Coach, Student


class StudentRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Student]:
        ...

    @abstractmethod
    def get_by_id(self, student_id: int) -> Student | None:
        ...

    @abstractmethod
    def add(self, student: Student) -> Student:
        ...

    @abstractmethod
    def update_remaining_hours(self, student_id: int, hours: float) -> Student | None:
        ...

    @abstractmethod
    def next_id(self) -> int:
        ...


class CoachRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Coach]:
        ...

    @abstractmethod
    def get_by_id(self, coach_id: int) -> Coach | None:
        ...

    @abstractmethod
    def add(self, coach: Coach) -> Coach:
        ...

    @abstractmethod
    def update_active(self, coach_id: int, active: bool) -> Coach | None:
        ...

    @abstractmethod
    def next_id(self) -> int:
        ...


class AppointmentRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Appointment]:
        ...

    @abstractmethod
    def list_by_status(self, status: AppointmentStatus) -> list[Appointment]:
        ...

    @abstractmethod
    def list_by_student(self, student_id: int) -> list[Appointment]:
        ...

    @abstractmethod
    def list_by_coach(self, coach_id: int) -> list[Appointment]:
        ...

    @abstractmethod
    def get_by_id(self, appointment_id: int) -> Appointment | None:
        ...

    @abstractmethod
    def add(self, appointment: Appointment) -> Appointment:
        ...

    @abstractmethod
    def update(self, appointment: Appointment) -> Appointment | None:
        ...

    @abstractmethod
    def has_conflict(
        self,
        coach_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_id: int | None = None,
    ) -> bool:
        ...

    @abstractmethod
    def count_active_by_student(self, student_id: int) -> int:
        ...

    @abstractmethod
    def next_id(self) -> int:
        ...


class CancelRuleRepository(ABC):
    @abstractmethod
    def get(self) -> CancelRule:
        ...
