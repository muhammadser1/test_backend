# Pricing System API Documentation

This document covers all pricing-related endpoints in the General Institute System. The pricing system manages hourly rates for different subjects at various education levels.

## Base URL
```
/api/v1/pricing
```

---

## Overview

The pricing system is designed around three education levels:
- **Elementary** (ابتدائي) - `elementary`
- **Middle** (اعدادي) - `middle`
- **Secondary** (ثانوي) - `secondary`

Each subject can have different pricing for each education level and lesson type (individual vs. group).

---

## Public Endpoints (No Authentication Required)

### 1. Get All Pricing
**GET** `/api/v1/pricing/`

Retrieves all pricing information. This endpoint is publicly accessible.

**Response (200 OK):**
```json
{
  "total": 45,
  "pricing": [
    {
      "id": "pricing_id_1",
      "subject": "Arabic",
      "education_level": "elementary",
      "individual_price": 38.25,
      "group_price": 21.25
    },
    {
      "id": "pricing_id_2",
      "subject": "Arabic",
      "education_level": "middle",
      "individual_price": 45.0,
      "group_price": 25.0
    },
    {
      "id": "pricing_id_3",
      "subject": "Arabic",
      "education_level": "secondary",
      "individual_price": 54.0,
      "group_price": 30.0
    }
  ]
}
```

**Notes:**
- Returns all subjects with all education levels
- No authentication required
- Typically returns 45 entries (15 subjects × 3 levels)

---

### 2. Lookup Specific Price
**GET** `/api/v1/pricing/lookup/{subject}/{education_level}`

Look up the price for a specific subject and education level.

**Path Parameters:**
- `subject` (string): Subject name (e.g., "Arabic", "Mathematics")
- `education_level` (string): Education level (`elementary`, `middle`, or `secondary`)

**Query Parameters:**
- `lesson_type` (string, optional): Lesson type (`individual` or `group`). Default: `individual`

**Example Request:**
```
GET /api/v1/pricing/lookup/Arabic/secondary?lesson_type=individual
```

**Response (200 OK):**
```json
{
  "subject": "Arabic",
  "education_level": "secondary",
  "lesson_type": "individual",
  "price_per_hour": 54.0,
  "found": true
}
```

**Error Responses:**
- `404 Not Found`: Pricing not found for the specified subject and education level

---

## Admin-Only Endpoints

### 3. Create New Pricing
**POST** `/api/v1/pricing/`

Admin creates new pricing for a subject at a specific education level.

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Request Body:**
```json
{
  "subject": "Arabic",
  "education_level": "elementary",
  "individual_price": 38.25,
  "group_price": 21.25
}
```

**Required Fields:**
- `subject` (string): Subject name (1-100 characters)
- `education_level` (string): Education level (`elementary`, `middle`, or `secondary`)
- `individual_price` (float): Price per hour for individual lessons (must be > 0)
- `group_price` (float): Price per hour for group lessons (must be > 0)

**Response (201 Created):**
```json
{
  "id": "new_pricing_id",
  "subject": "Arabic",
  "education_level": "elementary",
  "individual_price": 38.25,
  "group_price": 21.25
}
```

**Error Responses:**
- `400 Bad Request`: Subject + education level combination already exists
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User is not an admin
- `422 Unprocessable Entity`: Validation errors

**Notes:**
- Subject names are automatically title-cased (e.g., "arabic" → "Arabic")
- Each subject + education level combination must be unique

---

### 4. Get Pricing by ID
**GET** `/api/v1/pricing/{pricing_id}`

Admin retrieves specific pricing by ID.

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Path Parameters:**
- `pricing_id` (string): The pricing ID

**Response (200 OK):**
```json
{
  "id": "pricing_id_1",
  "subject": "Mathematics",
  "education_level": "middle",
  "individual_price": 50.0,
  "group_price": 30.0
}
```

**Error Responses:**
- `404 Not Found`: Pricing not found
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User is not an admin

---

### 5. Update Pricing
**PUT** `/api/v1/pricing/{pricing_id}`

Admin updates existing pricing.

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Path Parameters:**
- `pricing_id` (string): The pricing ID

**Request Body (all fields optional):**
```json
{
  "subject": "Mathematics",
  "education_level": "secondary",
  "individual_price": 60.0,
  "group_price": 40.0
}
```

**Response (200 OK):**
```json
{
  "id": "pricing_id_1",
  "subject": "Mathematics",
  "education_level": "secondary",
  "individual_price": 60.0,
  "group_price": 40.0
}
```

**Error Responses:**
- `400 Bad Request`: New subject + education level combination already exists
- `404 Not Found`: Pricing not found
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User is not an admin

---

## Education Level Details

### Elementary (ابتدائي)
- Value: `elementary`
- Typical grades: 1-6
- Default pricing: 85% of base price
- Lower complexity subjects

### Middle (اعدادي)
- Value: `middle`
- Typical grades: 7-9
- Default pricing: 100% of base price (baseline)
- Intermediate complexity

### Secondary (ثانوي)
- Value: `secondary`
- Typical grades: 10-12
- Default pricing: 120% of base price
- Advanced subjects, exam preparation

---

## Example Workflows

### For Frontend/Public Users:

**Get all available pricing:**
```bash
GET /api/v1/pricing/
```

**Check price for specific subject:**
```bash
GET /api/v1/pricing/lookup/Arabic/secondary?lesson_type=individual
```

### For Admins:

**Add a new subject:**
```bash
POST /api/v1/pricing/
{
  "subject": "Islamic Studies",
  "education_level": "middle",
  "individual_price": 45.0,
  "group_price": 25.0
}
```

**Update pricing:**
```bash
PUT /api/v1/pricing/{pricing_id}
{
  "individual_price": 55.0,
  "group_price": 32.0
}
```

---

## Notes

- **Public Access**: Most endpoints are publicly accessible for transparency
- **Admin Controls**: Only admins can create and update pricing
- **Unique Combinations**: Each subject + education level pair must be unique
- **Automatic Formatting**: Subject names are automatically title-cased
- **No Timestamps**: Pricing records do not track creation/update times for simplicity
- **No Currency Field**: System assumes single currency (can be extended later)
- **No Active/Inactive Status**: All pricing records are considered active

---

## Common Use Cases

### 1. Display Pricing Table
```javascript
// Fetch all pricing
const response = await fetch('/api/v1/pricing/');
const data = await response.json();

// Group by subject
const pricingBySubject = {};
data.pricing.forEach(p => {
  if (!pricingBySubject[p.subject]) {
    pricingBySubject[p.subject] = {};
  }
  pricingBySubject[p.subject][p.education_level] = {
    individual: p.individual_price,
    group: p.group_price
  };
});
```

### 2. Calculate Lesson Cost
```javascript
// Get price for Arabic, secondary, individual
const response = await fetch('/api/v1/pricing/lookup/Arabic/secondary?lesson_type=individual');
const data = await response.json();
const pricePerHour = data.price_per_hour;

// Calculate for 2-hour lesson
const totalCost = pricePerHour * 2;
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `400 Bad Request`: Invalid input or duplicate entry
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions (not admin)
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

