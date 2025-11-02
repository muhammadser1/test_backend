# User Authentication API Documentation

This document covers all user authentication endpoints in the General Institute System. These endpoints are available to all users (both admins and teachers).

## Base URL
```
/api/v1/user
```

---

## Authentication Endpoints

### 1. User Login
**POST** `/api/v1/user/login`

Allows users (both admins and teachers) to log in to the system.

**Request Body:**
```json
{
  "username": "admin",
  "password": "adminpassword"
}
```

**Required Fields:**
- `username` (string): User username
- `password` (string): User password

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "admin_id",
    "username": "admin",
    "role": "admin",
    "status": "active",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Invalid input
- `422 Unprocessable Entity`: Validation errors

---

### 2. User Logout
**POST** `/api/v1/user/logout`

Logs out the current user.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Not authenticated

---

### 3. Get Current User Info
**GET** `/api/v1/user/me`

Gets information about the currently authenticated user.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "admin_id",
  "username": "admin",
  "role": "admin",
  "status": "active",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "phone": "+1234567890",
  "birthdate": "1985-05-20",
  "last_login": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token

---

## Notes

- All authentication endpoints are available to all user types (admin and teacher)
- The `/me` endpoint returns different information based on user role
- Login updates the `last_login` timestamp
- Logout is optional but recommended for security
- Tokens are stateless and can be validated without database lookup
- These endpoints are **NOT admin-only** - they're for all users
