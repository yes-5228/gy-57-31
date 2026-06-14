from app.repositories.base import (
    AppointmentRepository,
    CancelRuleRepository,
    CoachRepository,
    StudentRepository,
)
from app.repositories.memory import (
    MemoryAppointmentRepository,
    MemoryCancelRuleRepository,
    MemoryCoachRepository,
    MemoryStudentRepository,
    seed_demo_data,
)

_student_repo: MemoryStudentRepository | None = None
_coach_repo: MemoryCoachRepository | None = None
_appointment_repo: MemoryAppointmentRepository | None = None
_cancel_rule_repo: MemoryCancelRuleRepository | None = None


def init_repositories() -> None:
    global _student_repo, _coach_repo, _appointment_repo, _cancel_rule_repo
    _student_repo = MemoryStudentRepository()
    _coach_repo = MemoryCoachRepository()
    _appointment_repo = MemoryAppointmentRepository()
    _cancel_rule_repo = MemoryCancelRuleRepository()
    seed_demo_data(_student_repo, _coach_repo, _appointment_repo)


def get_student_repo() -> StudentRepository:
    assert _student_repo is not None, "Repositories not initialized"
    return _student_repo


def get_coach_repo() -> CoachRepository:
    assert _coach_repo is not None, "Repositories not initialized"
    return _coach_repo


def get_appointment_repo() -> AppointmentRepository:
    assert _appointment_repo is not None, "Repositories not initialized"
    return _appointment_repo


def get_cancel_rule_repo() -> CancelRuleRepository:
    assert _cancel_rule_repo is not None, "Repositories not initialized"
    return _cancel_rule_repo
