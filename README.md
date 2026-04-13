# Online Learning Platform API

Backend API for an online learning platform with authentication, course management, enrollments, assignments, submissions, and reviews.

## Problem Statement

Online learning systems need a clear backend for managing users, courses, lessons, enrollments, and assessment workflows. Without a structured API, it becomes difficult to support role-based access, course publishing, student progress, and instructor review processes consistently.

## Features

- JWT-based authentication with access and refresh tokens
- Role-based access control for students, instructors, and admins
- Category and course management
- Lesson and assignment management inside courses
- Student enrollments and completion tracking
- Assignment submission and instructor grading
- Course review system
- Alembic migrations for database schema management
- Insomnia collection and planning documents in `docs/`

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/online_learning
JWT_SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379
```

5. Run migrations:

```bash
alembic upgrade head
```

## Usage

Start the development server:

```bash
uvicorn src.app.main:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

Useful endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/courses/`
- `POST /api/v1/enrollments/courses/{course_id}`
- `POST /api/v1/courses/{course_id}/assignments/`

## Screenshots

No screenshots are included yet. Add interface or API screenshots to `assets/` if required for submission.

## Technology Stack

- Python
- FastAPI
- SQLModel
- SQLAlchemy
- PostgreSQL
- Redis
- Alembic
- JWT authentication

## Repository Structure

```text
project-root/
├── src/
├── docs/
├── tests/
├── assets/
├── README.md
├── AUDIT.md
├── .gitignore
├── LICENSE
├── alembic.ini
└── requirements.txt
```
