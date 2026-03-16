from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    # Import all models so SQLModel registers them
    import app.users.models  # noqa
    import app.categories.models  # noqa
    import app.courses.models  # noqa
    import app.lessons.models  # noqa
    import app.enrollments.models  # noqa
    import app.assignments.models  # noqa
    import app.submissions.models  # noqa
    import app.reviews.models  # noqa
    import app.auth.models  # noqa
