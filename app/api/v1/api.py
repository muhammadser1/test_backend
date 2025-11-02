from fastapi import APIRouter
from app.api.v1.endpoints import user, admin, lessons, payments, pricing, students
from app.core.config import config

api_router = APIRouter()

# User routes (auth + profile)
api_router.include_router(user.router, prefix="/user", tags=["User"])

# Admin routes
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Student routes (teachers and admins can view)
api_router.include_router(students.router, prefix="/students", tags=["Students"])

# Lesson routes
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])

# Payment routes
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])

# Pricing routes (admin management + public lookup)
api_router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])

# Admin routes - Dashboard/Statistics
from app.api.v1.endpoints import dashboard
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# Admin routes - Pricing Population
from app.api.v1.endpoints import populate_pricing
api_router.include_router(populate_pricing.router, prefix="/populate-pricing", tags=["Pricing Population"])
