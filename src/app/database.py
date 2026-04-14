from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.app.config import settings

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
    import src.app.users.models  # noqa
    import src.app.categories.models  # noqa
    import src.app.courses.models  # noqa
    import src.app.lessons.models  # noqa
    import src.app.enrollments.models  # noqa
    import src.app.assignments.models  # noqa
    import src.app.submissions.models  # noqa
    import src.app.reviews.models  # noqa
    import src.app.auth.models  # noqa
