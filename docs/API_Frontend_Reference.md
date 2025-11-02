# API Frontend Reference

Complete API documentation for frontend developers - General Institute System

**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** Most endpoints require JWT token in header: `Authorization: Bearer <token>`

---

## Authentication

### POST `/user/login`
**Login** - Get access token

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "username": "admin",
    "role": "admin",
    "status": "active",
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

---

### POST `/user/logout`
**Logout** - Logout user

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

### GET `/user/me`
**Get Current User** - Get authenticated user profile

**Response:**
```json
{
  "id": "user_id",
  "username": "admin",
  "role": "admin",
  "status": "active",
  "email": "admin@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "birthdate": "1990-01-15",
  "last_login": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### PUT `/user/me`
**Update Profile** - Update current user profile

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "email": "newemail@example.com"
}
```

**Response:** (Same as GET `/user/me`)

---

### PUT `/user/me/change-password`
**Change Password** - Change current user password

**Request:**
```json
{
  "old_password": "oldpass123",
  "new_password": "newpass123"
}
```

**Response:**
```json
{
  "message": "Password updated successfully"
}
```

---

## Admin - User Management

### POST `/admin/users`
**Create User** - Admin creates new user (teacher/admin)

**Request:**
```json
{
  "username": "teacher1",
  "password": "password123",
  "role": "teacher",
  "email": "teacher1@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1234567890",
  "birthdate": "1990-01-15"
}
```

**Response:**
```json
{
  "id": "user_id",
  "username": "teacher1",
  "role": "teacher",
  "status": "active",
  "email": "teacher1@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1234567890",
  "birthdate": "1990-01-15",
  "last_login": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### GET `/admin/users?role=teacher&status=active&skip=0&limit=10`
**Get All Users** - Get all users with filters

**Query Parameters:**
- `role` (optional): "teacher" or "admin"
- `status` (optional): "active", "inactive", "suspended"
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 10, max: 100)

**Response:**
```json
[
  {
    "id": "user_id_1",
    "username": "teacher1",
    "role": "teacher",
    "status": "active",
    "email": "teacher1@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+1234567890",
    "birthdate": "1990-01-15",
    "last_login": "2024-01-15T09:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### PUT `/admin/users/{user_id}`
**Update User** - Admin updates user information

**Request:**
```json
{
  "email": "newemail@example.com",
  "first_name": "Updated Name",
  "last_name": "Updated Last",
  "phone": "+9876543210",
  "role": "admin",
  "status": "active"
}
```

**Response:** (User object)

---

### DELETE `/admin/users/{user_id}`
**Deactivate User** - Admin deactivates user

**Response:**
```json
{
  "message": "User deactivated successfully",
  "user_id": "user_id",
  "status": "inactive"
}
```

---

### POST `/admin/users/{user_id}/reset-password`
**Reset Password** - Admin resets user password

**Request:**
```json
{
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successfully",
  "user_id": "user_id"
}
```

---

## Pricing

### GET `/pricing/`
**Get All Pricing** - Get all subject pricing (public, no auth)

**Response:**
```json
{
  "total": 45,
  "pricing": [
    {
      "id": "pricing_id",
      "subject": "Mathematics",
      "education_level": "elementary",
      "individual_price": 42.5,
      "group_price": 25.5
    }
  ]
}
```

---

### GET `/pricing/lookup/{subject}/{education_level}?lesson_type=individual`
**Lookup Price** - Get price for specific subject/level (public)

**Response:**
```json
{
  "subject": "Mathematics",
  "education_level": "elementary",
  "lesson_type": "individual",
  "price_per_hour": 42.5,
  "found": true
}
```

---

### POST `/pricing/`
**Create Pricing** - Admin creates new pricing

**Request:**
```json
{
  "subject": "Arabic",
  "education_level": "elementary",
  "individual_price": 38.25,
  "group_price": 21.25
}
```

**Response:** (Pricing object)

---

### PUT `/pricing/{pricing_id}`
**Update Pricing** - Admin updates pricing

**Request:**
```json
{
  "individual_price": 45.0,
  "group_price": 30.0
}
```

**Response:** (Pricing object)

---

## Lessons

### POST `/lessons/submit`
**Submit Lesson** - Teacher creates new lesson (starts as pending)

**Request:**
```json
{
  "subject": "Mathematics",
  "education_level": "elementary",
  "lesson_type": "individual",
  "scheduled_date": "2024-01-20T14:00:00Z",
  "duration_minutes": 60,
  "max_students": 1,
  "students": [
    {
      "student_name": "John Doe",
      "student_email": "john@example.com"
    }
  ]
}
```

**Response:**
```json
{
  "id": "lesson_id",
  "teacher_id": "teacher_id",
  "teacher_name": "Jane Smith",
  "subject": "Mathematics",
  "education_level": "elementary",
  "lesson_type": "individual",
  "scheduled_date": "2024-01-20T14:00:00Z",
  "duration_minutes": 60,
  "max_students": 1,
  "status": "pending",
  "students": [...],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### GET `/lessons/my-lessons?lesson_type=individual&lesson_status=pending&month=1&year=2024`
**Get My Lessons** - Teacher gets own lessons with filters

**Query Parameters:**
- `lesson_type` (optional): "individual" or "group"
- `lesson_status` (optional): "pending", "approved", "rejected", "completed", "cancelled"
- `student_name` (optional): Filter by student name
- `month` (optional): 1-12
- `year` (optional): 2000-2100
- `skip` (optional): Pagination offset
- `limit` (optional): Results per page (max: 1000)

**Response:**
```json
{
  "total_lessons": 10,
  "total_hours": 15.5,
  "lessons": [...]
}
```

---

### GET `/lessons/summary`
**Get Lessons Summary** - Teacher gets detailed summary grouped by subject/type

**Response:**
```json
{
  "overall": {
    "total_lessons": 50,
    "total_hours": 75.5,
    "individual_lessons": 30,
    "individual_hours": 45.0,
    "group_lessons": 20,
    "group_hours": 30.5
  },
  "by_subject": {
    "Mathematics": {
      "total_lessons": 20,
      "total_hours": 30.0,
      "individual": {
        "lessons": 15,
        "hours": 22.5,
        "students": 15,
        "pending": 2,
        "completed": 10,
        "cancelled": 3
      },
      "group": {
        "lessons": 5,
        "hours": 7.5,
        "students": 20,
        "pending": 1,
        "completed": 3,
        "cancelled": 1
      }
    }
  }
}
```

---

### PUT `/lessons/update-lesson/{lesson_id}`
**Update Lesson** - Teacher updates own lesson (only if pending)

**Request:**
```json
{
  "subject": "Mathematics",
  "duration_minutes": 90,
  "scheduled_date": "2024-01-21T15:00:00Z"
}
```

**Response:** (Lesson object)

---

### DELETE `/lessons/delete-lesson/{lesson_id}`
**Delete Lesson** - Teacher deletes own lesson (only pending)

**Response:**
```json
{
  "message": "Lesson cancelled successfully"
}
```

---

### GET `/lessons/{lesson_id}`
**Get Lesson by ID** - Get specific lesson

**Response:** (Lesson object)

---

## Admin - Lesson Management

### GET `/lessons/admin/all?teacher_id=xxx&student_name=John&status=pending&month=1&year=2024`
**Get All Lessons (Admin)** - Admin views all lessons with filters

**Query Parameters:**
- `teacher_id` (optional): Filter by teacher
- `student_name` (optional): Filter by student
- `status` (optional): "pending", "approved", "rejected", "completed", "cancelled"
- `month` (optional): 1-12
- `year` (optional): 2000-2100
- `skip`, `limit` (optional): Pagination

**Response:**
```json
{
  "total_lessons": 100,
  "total_hours": 150.5,
  "lessons": [...]
}
```

---

### PUT `/lessons/admin/approve/{lesson_id}`
**Approve Lesson** - Admin approves pending lesson

**Response:** (Updated lesson object with status="approved")

---

### PUT `/lessons/admin/reject/{lesson_id}`
**Reject Lesson** - Admin rejects pending lesson

**Response:** (Updated lesson object with status="rejected")

---

## Students

### POST `/students/`
**Create Student** - Admin creates new student

**Request:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "birthdate": "2010-05-15",
  "notes": "Special needs"
}
```

**Response:**
```json
{
  "id": "student_id",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "birthdate": "2010-05-15",
  "notes": "Special needs",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### GET `/students/?include_inactive=false`
**Get All Students** - Get all students

**Query Parameters:**
- `include_inactive` (optional): true/false (default: false)

**Response:**
```json
{
  "total": 50,
  "students": [...]
}
```

---

### GET `/students/search?name=John`
**Search Students** - Search students by name

**Response:**
```json
{
  "total": 5,
  "students": [...]
}
```

---

### GET `/students/{student_id}`
**Get Student by ID** - Get specific student

**Response:** (Student object)

---

### PUT `/students/{student_id}`
**Update Student** - Admin updates student

**Request:**
```json
{
  "full_name": "John Doe Updated",
  "phone": "+9876543210"
}
```

**Response:** (Student object)

---

### DELETE `/students/{student_id}`
**Delete Student** - Admin deletes student (soft delete)

**Response:** 204 No Content

---

## Payments

### POST `/payments/`
**Create Payment** - Admin adds student payment

**Request:**
```json
{
  "student_name": "John Doe",
  "student_email": "john@example.com",
  "amount": 150.0,
  "payment_date": "2024-01-15T10:00:00Z",
  "lesson_id": "lesson_id",
  "notes": "Payment for January lessons"
}
```

**Response:**
```json
{
  "id": "payment_id",
  "student_name": "John Doe",
  "student_email": "john@example.com",
  "amount": 150.0,
  "payment_date": "2024-01-15T10:00:00Z",
  "lesson_id": "lesson_id",
  "notes": "Payment for January lessons",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### GET `/payments/?month=1&year=2024&student_name=John`
**Get Payments** - Admin gets payments with filters

**Query Parameters:**
- `month` (optional): 1-12 (requires year)
- `year` (optional): 2000-2100
- `student_name` (optional): Filter by student

**Response:**
```json
{
  "total_payments": 50,
  "total_amount": 7500.0,
  "payments": [...],
  "filter": {
    "month": 1,
    "year": 2024,
    "note": "Filtered by month and year"
  }
}
```

---

### GET `/payments/student/{student_name}`
**Get Student Payments** - Get all payments for student

**Response:**
```json
{
  "student_name": "John Doe",
  "total_payments": 10,
  "total_amount": 1500.0,
  "payments": [...]
}
```

---

### GET `/payments/student/{student_name}/total`
**Get Student Total** - Quick summary of student payments

**Response:**
```json
{
  "student_name": "John Doe",
  "total_payments": 10,
  "total_amount": 1500.0,
  "currency": "USD"
}
```

---

### GET `/payments/student/{student_name}/cost-summary?month=1&year=2024`
**Get Student Cost Summary** - Lessons cost vs paid amount

**Query Parameters:**
- `month` (optional): 1-12 (requires year)
- `year` (optional): 2000-2100

**Response:**
```json
{
  "student_name": "John Doe",
  "total_lessons_cost": 1800.0,
  "total_paid": 1500.0,
  "outstanding_balance": 300.0,
  "lessons_count": 12,
  "payments_count": 10,
  "currency": "USD",
  "filter": {
    "month": 1,
    "year": 2024,
    "note": "Statistics filtered by month and year"
  }
}
```

---

### DELETE `/payments/{payment_id}`
**Delete Payment** - Admin deletes payment

**Response:** 204 No Content

---

## Dashboard & Statistics

### GET `/dashboard/stats?month=1&year=2024`
**Dashboard Statistics** - Admin dashboard overview

**Query Parameters:**
- `month` (optional): 1-12
- `year` (optional): 2000-2100

**Response:**
```json
{
  "users": {
    "total_teachers": 15,
    "total_admins": 3,
    "total_users": 18
  },
  "students": {
    "total_students": 50
  },
  "lessons": {
    "total_lessons": 200,
    "pending_lessons": 20,
    "completed_lessons": 150,
    "cancelled_lessons": 30
  },
  "payments": {
    "total_payments": 100,
    "total_revenue": 15000.0
  },
  "pricing": {
    "active_subjects": 45
  },
  "filter": {
    "month": 1,
    "year": 2024,
    "note": "Statistics filtered by month and year"
  }
}
```

---

### GET `/dashboard/stats/teachers?year=2024&month=1&status=active&search=john`
**Get Teachers Statistics** - Detailed teacher statistics

**Query Parameters:**
- `month` (optional): 1-12
- `year` (optional): 2000-2100
- `search` (optional): Search by name/username
- `status` (optional): "active", "inactive", "suspended" (default: "active")

**Response:**
```json
{
  "total_teachers": 15,
  "teachers": [
    {
      "teacher_id": "teacher_id",
      "teacher_name": "Jane Smith",
      "username": "teacher1",
      "email": "teacher1@example.com",
      "phone": "+1234567890",
      "status": "active",
      "total_lessons": 50,
      "pending_lessons": 5,
      "completed_lessons": 40,
      "cancelled_lessons": 5,
      "total_hours": 75.5,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-15T09:00:00Z"
    }
  ],
  "filters": {
    "status": "active",
    "lesson_date_filter": {
      "year": 2024,
      "note": "Lesson statistics filtered by year"
    }
  }
}
```

---

### GET `/dashboard/stats/students`
**Get Students Statistics** - Detailed student statistics

**Response:**
```json
{
  "total_students": 50,
  "students": [
    {
      "student_id": "student_id",
      "student_name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "total_payments": 10,
      "total_paid": 1500.0
    }
  ]
}
```

---

### GET `/dashboard/stats/lessons?month=1&year=2024`
**Get Lessons Statistics** - Detailed lesson statistics

**Response:**
```json
{
  "by_type": {
    "individual_lessons": 100,
    "group_lessons": 50,
    "total_lessons": 150
  },
  "by_status": {
    "pending_lessons": 20,
    "approved_lessons": 30,
    "rejected_lessons": 5,
    "completed_lessons": 80,
    "cancelled_lessons": 15,
    "total_lessons": 150
  },
  "total_hours": 225.5,
  "filter": {
    "month": 1,
    "year": 2024,
    "note": "Statistics filtered by month and year"
  }
}
```

---

### GET `/dashboard/teacher-earnings/{teacher_id}?month=1&year=2024`
**Get Teacher Earnings** - Teacher earnings breakdown by subject

**Response:**
```json
{
  "teacher_id": "teacher_id",
  "teacher_name": "Jane Smith",
  "month": 1,
  "year": 2024,
  "total_hours": 75.5,
  "total_earnings": 3375.0,
  "total_lessons": 50,
  "by_subject": [
    {
      "subject": "Mathematics",
      "education_level": "elementary",
      "lesson_type": "individual",
      "total_hours": 20.0,
      "price_per_hour": 42.5,
      "total_earnings": 850.0,
      "lesson_count": 15
    }
  ]
}
```

---

### GET `/dashboard/student-hours/{student_name}?month=1&year=2024`
**Get Student Hours Summary** - Student hours breakdown

**Response:**
```json
{
  "student_name": "John Doe",
  "individual_hours": 30.0,
  "group_hours": 15.5,
  "total_hours": 45.5,
  "individual_lessons": 20,
  "group_lessons": 10,
  "total_lessons": 30,
  "filter": {
    "month": 1,
    "year": 2024,
    "note": "Statistics filtered by month and year"
  }
}
```

---

## Lesson Status Values

- `pending` - Waiting for admin approval
- `approved` - Admin approved the lesson
- `rejected` - Admin rejected the lesson
- `completed` - Lesson finished
- `cancelled` - Lesson cancelled/deleted

## Education Level Values

- `elementary` - ابتدائي
- `middle` - اعدادي
- `secondary` - ثانوي

## Lesson Type Values

- `individual` - Individual lesson
- `group` - Group lesson

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid input or duplicate entry
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors

**Error Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Authentication Example (JavaScript)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/user/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const { access_token } = await loginResponse.json();

// Use token in subsequent requests
const response = await fetch('http://localhost:8000/api/v1/user/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

---

## Notes

- All dates are in ISO 8601 format (UTC)
- Token expiration: Check your server configuration
- Pagination: Use `skip` and `limit` for paginated endpoints
- Filtering: Most list endpoints support multiple filter parameters
- Empty arrays/lists are returned as `[]`, not `null`

