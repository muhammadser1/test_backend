# Admin User Management API Documentation

This document covers all admin endpoints for user management in the General Institute System.

## Authentication

All admin endpoints require authentication with a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
/api/v1/admin
```

---

## User Management Endpoints

### 1. Create User
**POST** `/api/v1/admin/users`

Creates a new user (teacher or admin) in the system.

**Request Body:**
```json
{
  "username": "newteacher",
  "password": "password123",
  "role": "teacher",
  "email": "teacher@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "birthdate": "1990-01-15"
}
```

**Required Fields:**
- `username` (string): Unique username
- `password` (string): Password (min 6 characters)
- `role` (string): Either "teacher" or "admin"

**Optional Fields:**
- `email` (string): Email address (required for admin users)
- `first_name` (string): First name
- `last_name` (string): Last name
- `phone` (string): Phone number
- `birthdate` (string): Date in YYYY-MM-DD format

**Response (201 Created):**
```json
{
  "id": "user_id_here",
  "username": "newteacher",
  "role": "teacher",
  "status": "active",
  "email": "teacher@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "birthdate": "1990-01-15",
  "last_login": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Username/email already exists, missing required fields
- `403 Forbidden`: Not an admin user
- `422 Unprocessable Entity`: Invalid input data

---

### 2. Get All Users
**GET** `/api/v1/admin/users`

Retrieves a list of all users with optional filtering and pagination.

**Query Parameters:**
- `role` (optional): Filter by role ("teacher" or "admin")
- `status` (optional): Filter by status ("active", "inactive", "suspended")
- `skip` (optional): Number of users to skip (default: 0)
- `limit` (optional): Maximum users to return (default: 10, max: 100)

**Example Request:**
```
GET /api/v1/admin/users?role=teacher&status=active&skip=0&limit=20
```

**Response (200 OK):**
```json
[
  {
    "id": "user_id_1",
    "username": "teacher1",
    "role": "teacher",
    "status": "active",
    "email": "teacher1@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "last_login": "2024-01-15T09:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "user_id_2",
    "username": "admin1",
    "role": "admin",
    "status": "active",
    "email": "admin1@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+0987654321",
    "last_login": "2024-01-15T08:30:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

**Error Responses:**
- `403 Forbidden`: Not an admin user
- `422 Unprocessable Entity`: Invalid query parameters

---

### 3. Get User by ID
**GET** `/api/v1/admin/users/{user_id}`

Retrieves detailed information about a specific user.

**Path Parameters:**
- `user_id` (string): The unique identifier of the user

**Example Request:**
```
GET /api/v1/admin/users/507f1f77bcf86cd799439011
```

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "username": "teacher1",
  "role": "teacher",
  "status": "active",
  "email": "teacher1@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "birthdate": "1990-01-15",
  "last_login": "2024-01-15T09:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `403 Forbidden`: Not an admin user

---

### 4. Update User
**PUT** `/api/v1/admin/users/{user_id}`

Updates user information. Only provided fields will be updated.

**Path Parameters:**
- `user_id` (string): The unique identifier of the user

**Request Body:**
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

**All fields are optional:**
- `username` (string): New username (must be unique)
- `email` (string): New email (must be unique)
- `first_name` (string): New first name
- `last_name` (string): New last name
- `phone` (string): New phone number
- `role` (string): New role ("teacher" or "admin")
- `status` (string): New status ("active", "inactive", "suspended")

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "username": "teacher1",
  "role": "admin",
  "status": "active",
  "email": "newemail@example.com",
  "first_name": "Updated Name",
  "last_name": "Updated Last",
  "phone": "+9876543210",
  "birthdate": "1990-01-15",
  "last_login": "2024-01-15T09:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Username/email already exists
- `404 Not Found`: User not found
- `403 Forbidden`: Not an admin user

---

### 5. Deactivate User
**DELETE** `/api/v1/admin/users/{user_id}`

Deactivates a user (soft delete). The user is not permanently deleted but marked as inactive.

**Path Parameters:**
- `user_id` (string): The unique identifier of the user

**Example Request:**
```
DELETE /api/v1/admin/users/507f1f77bcf86cd799439011
```

**Response (200 OK):**
```json
{
  "message": "User deactivated successfully",
  "user_id": "507f1f77bcf86cd799439011",
  "status": "inactive"
}
```

**Error Responses:**
- `400 Bad Request`: User is already inactive
- `404 Not Found`: User not found
- `403 Forbidden`: Not an admin user

---

### 6. Reset User Password
**POST** `/api/v1/admin/users/{user_id}/reset-password`

Resets a user's password to a new value.

**Path Parameters:**
- `user_id` (string): The unique identifier of the user

**Request Body:**
```json
{
  "new_password": "newpassword123"
}
```

**Required Fields:**
- `new_password` (string): New password (min 6 characters)

**Response (200 OK):**
```json
{
  "message": "Password reset successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Password too short
- `403 Forbidden`: Not an admin user

---


## Notes

- All admin endpoints require admin role authentication
- User IDs are MongoDB ObjectIds (24-character hex strings)
- Dates are returned in ISO 8601 format (UTC)
- Passwords are automatically hashed before storage
- Deactivated users are not permanently deleted (soft delete)
- Email addresses must be unique across all users
- Usernames must be unique across all users
- Admin users must have an email address
