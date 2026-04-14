from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.auth.routes import router as auth_router
from src.app.users.routes import router as users_router
from src.app.categories.routes import router as categories_router
from src.app.courses.routes import router as courses_router
from src.app.lessons.routes import router as lessons_router
from src.app.enrollments.routes import router as enrollments_router
from src.app.assignments.routes import router as assignments_router
from src.app.submissions.routes import router as submissions_router
from src.app.reviews.routes import router as reviews_router

# Import all models so SQLModel registers them before anything else
import src.app.users.models  # noqa
import src.app.categories.models  # noqa
import src.app.courses.models  # noqa
import src.app.lessons.models  # noqa
import src.app.enrollments.models  # noqa
import src.app.assignments.models  # noqa
import src.app.submissions.models  # noqa
import src.app.reviews.models  # noqa
import src.app.auth.models  # noqa

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
