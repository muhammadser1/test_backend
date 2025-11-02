# API Endpoints Reference

Complete list of all API endpoints in the General Institute System.

---

## User Authentication (`/api/v1/user`)

### POST `/api/v1/user/login`
**User login** - Returns access token and user info for admins and teachers

### POST `/api/v1/user/logout`
**User logout** - Logs out current user (client should delete token)

### GET `/api/v1/user/me`
**Get current user info** - Returns full profile of authenticated user

### PUT `/api/v1/user/me`
**Update profile** - Update current user's profile (name, phone, email)

### PUT `/api/v1/user/me/change-password`
**Change password** - Change current user's password (requires old password)

---

## Admin User Management (`/api/v1/admin`)

### POST `/api/v1/admin/users`
**Create user** - Admin creates a new user (teacher or admin)

### GET `/api/v1/admin/users`
**Get all users** - Admin retrieves all users with optional filters (role, status, pagination)

### GET `/api/v1/admin/users/{user_id}`
**Get user by ID** - Admin retrieves detailed information about a specific user

### PUT `/api/v1/admin/users/{user_id}`
**Update user** - Admin updates user information (email, name, role, status, etc.)

### DELETE `/api/v1/admin/users/{user_id}`
**Deactivate user** - Admin deactivates a user (soft delete, marks as inactive)

### POST `/api/v1/admin/users/{user_id}/reset-password`
**Reset user password** - Admin resets a user's password to a new value

---

## Pricing (`/api/v1/pricing`)

### POST `/api/v1/pricing/`
**Create pricing** - Admin creates new subject pricing for an education level

### GET `/api/v1/pricing/`
**Get all pricing** - Get all pricing information (public endpoint, no auth required)

### GET `/api/v1/pricing/{pricing_id}`
**Get pricing by ID** - Admin retrieves specific pricing by ID

### PUT `/api/v1/pricing/{pricing_id}`
**Update pricing** - Admin updates existing pricing (subject, level, prices)

### GET `/api/v1/pricing/lookup/{subject}/{education_level}`
**Lookup price** - Look up price for a specific subject and education level (public)

---

## Lessons (`/api/v1/lessons`)

### POST `/api/v1/lessons/submit`
**Submit lesson** - Teacher creates a new lesson (individual or group) - starts as pending

### GET `/api/v1/lessons/my-lessons`
**Get my lessons** - Teacher gets their own lessons with filters (type, status, student, date) and total hours

### GET `/api/v1/lessons/summary`
**Get lessons summary** - Get detailed summary of lessons grouped by subject and type with statistics

### PUT `/api/v1/lessons/update-lesson/{lesson_id}`
**Update lesson** - Teacher updates their own lesson (only if status is pending)

### DELETE `/api/v1/lessons/delete-lesson/{lesson_id}`
**Delete lesson** - Teacher deletes their own lesson (soft delete - changes status to cancelled, only pending lessons)

### GET `/api/v1/lessons/{lesson_id}`
**Get lesson by ID** - Get a specific lesson by ID (teachers see own, admins see any)

### GET `/api/v1/lessons/admin/all`
**Get all lessons (Admin)** - Admin views all lessons with filters (teacher, student, status, month, year)

### PUT `/api/v1/lessons/admin/approve/{lesson_id}`
**Approve lesson** - Admin approves a pending lesson

### PUT `/api/v1/lessons/admin/reject/{lesson_id}`
**Reject lesson** - Admin rejects a pending lesson

---

## Payments (`/api/v1/payments`)

### POST `/api/v1/payments/`
**Create payment** - Admin adds a new student payment

### GET `/api/v1/payments/`
**Get payments** - Admin gets student payments with flexible filtering (month, year, student name)

### GET `/api/v1/payments/student/{student_name}`
**Get student payments** - Admin gets all payments for a specific student with total amount

### GET `/api/v1/payments/student/{student_name}/total`
**Get student total** - Admin gets total amount paid by a specific student (quick summary)

### GET `/api/v1/payments/student/{student_name}/cost-summary`
**Get student cost summary** - Admin gets student cost summary (lessons cost vs paid amount, outstanding balance) with optional month/year filter

### DELETE `/api/v1/payments/{payment_id}`
**Delete payment** - Admin deletes a payment record

---

## Students (`/api/v1/students`)

### POST `/api/v1/students/`
**Create student** - Admin creates a new student

### GET `/api/v1/students/`
**Get all students** - Get all students (teachers and admins can view, optional: include inactive)

### GET `/api/v1/students/search`
**Search students** - Search students by name (case-insensitive, partial match)

### GET `/api/v1/students/{student_id}`
**Get student by ID** - Get student by ID (teachers and admins can view)

### PUT `/api/v1/students/{student_id}`
**Update student** - Admin updates student information

### DELETE `/api/v1/students/{student_id}`
**Delete student** - Admin deletes student (soft delete - marks as inactive)

---

## Dashboard & Statistics (`/api/v1/dashboard`)

### GET `/api/v1/dashboard/stats`
**Dashboard statistics** - Admin dashboard overview with total counts (teachers, students, lessons, payments, revenue) with optional month/year filter

### GET `/api/v1/dashboard/stats/teachers`
**Get teachers statistics** - Get detailed statistics about teachers with lesson counts, hours, and optional filters (month, year, search, status)

### GET `/api/v1/dashboard/stats/students`
**Get students statistics** - Get detailed statistics about students with payment information

### GET `/api/v1/dashboard/stats/lessons`
**Get lessons statistics** - Get detailed statistics about lessons by type, status, and total hours with optional month/year filter

### GET `/api/v1/dashboard/teacher-earnings/{teacher_id}`
**Get teacher earnings** - Admin gets teacher earnings breakdown by subject with total hours, price per hour, and total payment, with optional month/year filter

### GET `/api/v1/dashboard/student-hours/{student_name}`
**Get student hours summary** - Admin gets student hours summary (individual vs group) with optional month/year filter

---

## Pricing Population (`/api/v1/pricing`)

### POST `/api/v1/pricing/populate-defaults`
**Populate default pricing** - Populates database with default subjects for all education levels (45 entries: 15 subjects × 3 levels)

### POST `/api/v1/pricing/populate-custom`
**Populate custom pricing** - Admin populates custom subjects with specific pricing

### GET `/api/v1/pricing/default-subjects`
**Get default subjects list** - Returns the list of default subjects that can be populated

---

## Notes

- **Authentication**: Most endpoints require JWT token in `Authorization: Bearer <token>` header
- **Public Endpoints**: Some pricing endpoints are publicly accessible
- **Role-based Access**: 
  - `Admin`: Full access to all endpoints
  - `Teacher`: Access to lessons management and limited read access
- **Base URL**: All endpoints are prefixed with `/api/v1/`
