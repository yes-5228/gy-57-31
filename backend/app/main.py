from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import init_repositories
from app.routes import appointments, coaches, dashboard, students

app = FastAPI(title="Driving School Booking API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_repositories()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(coaches.router, prefix="/api/coaches", tags=["coaches"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
