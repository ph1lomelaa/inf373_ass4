# Online Learning Platform — Plan

## 1. Entities

1. **User** — registered person (student, instructor, admin)
2. **Category** — course topic category (e.g. Programming, Design)
3. **Course** — educational course created by an instructor
4. **Lesson** — individual lesson/unit inside a course
5. **Enrollment** — student's registration in a course
6. **Assignment** — task/homework tied to a course
7. **Submission** — student's answer to an assignment
8. **Review** — rating + comment left by a student for a course

---

## 2. Functional Requirements (User Stories)

### User
- As a **Guest**, I can register an account.
- As a **Guest**, I can log in.
- As a **User** (auth), I can view my own profile.
- As a **User** (auth), I can update my own profile.
- As a **User** (auth), I can log out.
- As an **Admin** (auth, role=admin), I can list all users.
- As an **Admin** (auth, role=admin), I can deactivate/ban a user.
- As an **Admin** (auth, role=admin), I can change a user's role.

### Category
- As a **Guest**, I can list all categories.
- As a **Guest**, I can view a category by ID.
- As an **Admin** (auth, role=admin), I can create a category.
- As an **Admin** (auth, role=admin), I can update a category.
- As an **Admin** (auth, role=admin), I can delete a category.

### Course
- As a **Guest**, I can list all published courses (filter by category, search by title, sort by price/date).
- As a **Guest**, I can view a published course's details.
- As an **Instructor** (auth, role=instructor), I can create a course.
- As an **Instructor** (auth, role=instructor), I can update my own course.
- As an **Instructor** (auth, role=instructor), I can publish/unpublish my own course.
- As an **Instructor** (auth, role=instructor), I can delete my own course.
- As an **Admin** (auth, role=admin), I can delete any course.
- As an **Admin** (auth, role=admin), I can list all courses (including unpublished).

### Lesson
- As a **Guest**, I can view the lesson list (titles only) for a published course.
- As an **Enrolled Student** (auth, enrolled in course), I can view full lesson content.
- As an **Instructor** (auth, role=instructor), I can add a lesson to my own course.
- As an **Instructor** (auth, role=instructor), I can update a lesson in my own course.
- As an **Instructor** (auth, role=instructor), I can delete a lesson from my own course.
- As an **Instructor** (auth, role=instructor), I can reorder lessons in my own course.

### Enrollment
- As a **Student** (auth, role=student), I can enroll in a published course.
- As a **Student** (auth), I can list my own enrollments.
- As a **Student** (auth, enrolled), I can mark my enrollment as completed.
- As a **Student** (auth, enrolled), I can cancel (unenroll from) a course.
- As an **Instructor** (auth, role=instructor), I can list enrollments for my own course.
- As an **Admin** (auth, role=admin), I can list all enrollments.

### Assignment
- As a **Guest**, I can view assignments (title + due date) for a published course.
- As an **Enrolled Student** (auth, enrolled), I can view full assignment details.
- As an **Instructor** (auth, role=instructor), I can create an assignment for my own course.
- As an **Instructor** (auth, role=instructor), I can update an assignment in my own course.
- As an **Instructor** (auth, role=instructor), I can delete an assignment from my own course.

### Submission
- As an **Enrolled Student** (auth, enrolled), I can submit an assignment.
- As an **Enrolled Student** (auth, enrolled), I can view my own submissions.
- As an **Instructor** (auth, role=instructor), I can view all submissions for assignments in my course.
- As an **Instructor** (auth, role=instructor), I can grade a submission (set score + feedback).

### Review
- As a **Guest**, I can list reviews for a course.
- As an **Enrolled Student** (auth, enrolled), I can create a review for a course.
- As an **Enrolled Student** (auth), I can update my own review.
- As an **Enrolled Student** (auth), I can delete my own review.
- As an **Admin** (auth, role=admin), I can delete any review.

---

## 3. ERD

![ERD Diagram](erd.png)

**Entities & Relationships:**

| Entity | PK | Key FK | Key Attributes |
|---|---|---|---|
| users | id (UUID) | — | email, username, hashed_password, role, is_active |
| categories | id (UUID) | — | name, description |
| courses | id (UUID) | instructor_id→users, category_id→categories | title, description, price, is_published |
| lessons | id (UUID) | course_id→courses | title, content, video_url, order |
| enrollments | id (UUID) | student_id→users, course_id→courses | status, enrolled_at, completed_at |
| assignments | id (UUID) | course_id→courses | title, description, due_date, max_score |
| submissions | id (UUID) | student_id→users, assignment_id→assignments | content, score, feedback, status, submitted_at |
| reviews | id (UUID) | student_id→users, course_id→courses | rating, comment, created_at |
| refresh_tokens | id (UUID) | user_id→users | token, expires_at |

**Relationship types:**
- users 1 ——< courses (one instructor has many courses)
- categories 1 ——< courses (one category has many courses)
- courses 1 ——< lessons (one course has many lessons)
- courses 1 ——< enrollments
- users 1 ——< enrollments (one student has many enrollments)
- courses 1 ——< assignments
- assignments 1 ——< submissions
- users 1 ——< submissions
- courses 1 ——< reviews
- users 1 ——< reviews
- users 1 ——< refresh_tokens

---

## 4. Edge Cases

### Auth
- Register with already existing email → 409 Conflict
- Register with already existing username → 409 Conflict
- Login with wrong password → 401 Unauthorized
- Login with non-existent email → 401 Unauthorized
- Access protected endpoint with expired token → 401 Unauthorized
- Access protected endpoint with revoked/logged-out token → 401 Unauthorized
- Use access token in refresh endpoint → 400 Bad Request
- Use already-used/expired refresh token → 401 Unauthorized

### User
- Deactivated user tries to log in → 403 Forbidden
- User tries to update another user's profile → 403 Forbidden
- Admin changes role to invalid value → 422 Unprocessable Entity

### Category
- Create category with duplicate name → 409 Conflict
- Delete category that has courses assigned → 400 Bad Request (cannot delete with active courses)

### Course
- Instructor tries to update/delete another instructor's course → 403 Forbidden
- Instructor tries to publish a course that has no lessons → 400 Bad Request
- Guest tries to view an unpublished course → 404 Not Found
- Student tries to enroll in an unpublished course → 404 Not Found
- Delete a course → cascades to lessons, enrollments, assignments (+ submissions), reviews
- Create course with non-existent category_id → 404 Not Found

### Lesson
- Create lesson with `order` that already exists in the course → auto-shift or 409
- Instructor tries to modify lesson in another instructor's course → 403 Forbidden
- Enrolled student tries to access lesson of a course they cancelled enrollment → 403 Forbidden
- Non-enrolled user tries to access full lesson content → 403 Forbidden

### Enrollment
- Student tries to enroll in a course they're already actively enrolled in → 409 Conflict
- Student tries to enroll in a course they previously cancelled → allow (create new enrollment)
- Student tries to mark enrollment as completed when already completed → 400 Bad Request
- Student tries to cancel an already-cancelled enrollment → 400 Bad Request
- Instructor tries to enroll in a course → 403 Forbidden (instructors don't enroll)

### Assignment
- Instructor tries to create assignment for another instructor's course → 403 Forbidden
- Non-enrolled student tries to view assignment details → 403 Forbidden
- Delete assignment → cascades to all its submissions

### Submission
- Student submits an assignment after the due date → 400 Bad Request
- Student tries to submit the same assignment twice → 409 Conflict
- Student tries to submit assignment for a course they're not enrolled in → 403 Forbidden
- Instructor grades submission with score > max_score → 400 Bad Request
- Instructor tries to grade submission for another instructor's assignment → 403 Forbidden
- Non-instructor/non-owner tries to view all submissions → 403 Forbidden

### Review
- Student tries to review a course they're not enrolled in → 403 Forbidden
- Student tries to review the same course twice → 409 Conflict
- Student tries to update/delete another student's review → 403 Forbidden
- Rating outside 1–5 range → 422 Unprocessable Entity

---

## 5. Authentication Scenarios

Actions requiring `(auth)`:
- View/update own profile
- Enroll in a course
- View lesson full content (enrolled)
- View assignment details (enrolled)
- Submit an assignment
- View own submissions
- Create / update / delete a review
- Create / update / delete a course (instructor)
- Create / update / delete a lesson (instructor)
- Create / update / delete an assignment (instructor)
- Grade a submission (instructor)
- View enrollments / submissions for own course (instructor)
- All admin actions

Actions **not** requiring auth:
- Register / Login
- List categories, view a category
- List published courses, view a course
- List lesson titles for a course
- List reviews for a course
- View assignment titles/due dates for a course

---

## 6. Authorization Scenarios

| Role | Allowed Actions |
|---|---|
| **student** | Enroll, view enrolled content, submit, review |
| **instructor** | All student actions + create/manage own courses, lessons, assignments; grade submissions |
| **admin** | Everything + manage users, delete any course/review, list all data |

Specific rules:
- Only **instructors** can create courses, lessons, assignments
- Instructors can only modify **their own** courses/lessons/assignments
- Only **enrolled students** can view full lesson/assignment content, submit, and review
- Only **admin** can create categories, ban users, change roles
- A **student** cannot enroll in a course where they are the instructor
