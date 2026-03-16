from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.categories.routes import router as categories_router
from app.courses.routes import router as courses_router
from app.lessons.routes import router as lessons_router
from app.enrollments.routes import router as enrollments_router
from app.assignments.routes import router as assignments_router
from app.submissions.routes import router as submissions_router
from app.reviews.routes import router as reviews_router

# Import all models so SQLModel registers them before anything else
import app.users.models  # noqa
import app.categories.models  # noqa
import app.courses.models  # noqa
import app.lessons.models  # noqa
import app.enrollments.models  # noqa
import app.assignments.models  # noqa
import app.submissions.models  # noqa
import app.reviews.models  # noqa
import app.auth.models  # noqa

app = FastAPI(title="Online Learning Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(courses_router, prefix="/api/v1")
app.include_router(lessons_router, prefix="/api/v1")
app.include_router(enrollments_router, prefix="/api/v1")
app.include_router(assignments_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
