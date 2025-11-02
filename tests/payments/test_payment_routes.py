"""
Comprehensive tests for Payment routes/endpoints
Tests: Create payment, get monthly payments, filtering
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from app.models.user import User, UserRole, UserStatus
from app.models.payment import Payment
from app.core.security import get_password_hash, create_access_token


class TestCreatePaymentEndpoint:
    """Test POST /api/v1/payments/ - Create payment"""
    
    def test_admin_creates_payment_successfully(self, client, mock_db):
        """Test admin can create a new payment"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "John Doe",
                    "student_email": "john@example.com",
                    "amount": 150.50,
                    "payment_date": "2024-01-15T10:00:00",
                    "lesson_id": "lesson-123",
                    "notes": "First payment"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            
            assert data["student_name"] == "John Doe"
            assert data["student_email"] == "john@example.com"
            assert data["amount"] == 150.50
            assert data["lesson_id"] == "lesson-123"
            assert data["notes"] == "First payment"
            assert "id" in data
            assert "created_at" in data
            
            # Verify payment was saved to database
            payment_doc = mock_db["payments"].find_one({"student_name": "John Doe"})
            assert payment_doc is not None
            assert payment_doc["created_by"] == admin._id
    
    def test_create_payment_with_minimal_fields(self, client, mock_db):
        """Test creating payment with only required fields"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Minimal Student",
                    "amount": 100.0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["student_name"] == "Minimal Student"
            assert data["student_email"] is None
            assert data["lesson_id"] is None
            assert data["notes"] is None
    
    def test_create_payment_without_required_fields_fails(self, client, mock_db):
        """Test creating payment without required fields fails validation"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Missing student_name
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "amount": 100.0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            assert response.status_code == 422
            
            # Missing amount
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Test",
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            assert response.status_code == 422
            
            # Missing payment_date
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Test",
                    "amount": 100.0
                }
            )
            assert response.status_code == 422
    
    def test_create_payment_with_zero_amount_fails(self, client, mock_db):
        """Test creating payment with zero or negative amount fails"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Zero amount
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Test",
                    "amount": 0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            assert response.status_code == 422
            
            # Negative amount
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Test",
                    "amount": -100.0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            assert response.status_code == 422
    
    def test_teacher_cannot_create_payment(self, client, mock_db):
        """Test teacher cannot create payments"""
        teacher = User(
            username="teacher",
            hashed_password=get_password_hash("teacher123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(teacher.to_dict())
        
        token = create_access_token({
            "sub": teacher._id,
            "username": teacher.username,
            "role": teacher.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Test",
                    "amount": 100.0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            
            assert response.status_code == 403
            assert "Admin access required" in response.json()["detail"]


class TestGetMonthlyPaymentsEndpoint:
    """Test GET /api/v1/payments/ - Get monthly payments"""
    
    def test_admin_gets_monthly_payments(self, client, mock_db):
        """Test admin can get all payments for a specific month"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create payments in January 2024
        payment1 = Payment(
            student_name="Student 1",
            amount=100.0,
            payment_date=datetime(2024, 1, 10),
            created_by=admin._id
        )
        payment2 = Payment(
            student_name="Student 2",
            amount=200.0,
            payment_date=datetime(2024, 1, 20),
            created_by=admin._id
        )
        # Payment in different month
        payment3 = Payment(
            student_name="Student 3",
            amount=150.0,
            payment_date=datetime(2024, 2, 10),
            created_by=admin._id
        )
        
        mock_db["payments"].insert_one(payment1.to_dict())
        mock_db["payments"].insert_one(payment2.to_dict())
        mock_db["payments"].insert_one(payment3.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/payments/?month=1&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["month"] == 1
            assert data["year"] == 2024
            assert data["total_payments"] == 2  # Only January payments
            assert data["total_amount"] == 300.0  # 100 + 200
            assert len(data["payments"]) == 2
    
    def test_monthly_payments_calculates_total_correctly(self, client, mock_db):
        """Test monthly payments calculates total amount correctly"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create payments with decimal amounts
        payments_data = [
            ("S1", 99.99),
            ("S2", 150.50),
            ("S3", 200.25),
        ]
        
        for student_name, amount in payments_data:
            payment = Payment(
                student_name=student_name,
                amount=amount,
                payment_date=datetime(2024, 3, 15),
                created_by=admin._id
            )
            mock_db["payments"].insert_one(payment.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/payments/?month=3&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_amount"] == 450.74  # 99.99 + 150.50 + 200.25
    
    def test_filter_payments_by_student_name(self, client, mock_db):
        """Test filtering monthly payments by student name"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create payments with different student names
        payment1 = Payment(
            student_name="John Doe",
            amount=100.0,
            payment_date=datetime(2024, 4, 10),
            created_by=admin._id
        )
        payment2 = Payment(
            student_name="John Smith",
            amount=200.0,
            payment_date=datetime(2024, 4, 15),
            created_by=admin._id
        )
        payment3 = Payment(
            student_name="Jane Doe",
            amount=150.0,
            payment_date=datetime(2024, 4, 20),
            created_by=admin._id
        )
        
        mock_db["payments"].insert_one(payment1.to_dict())
        mock_db["payments"].insert_one(payment2.to_dict())
        mock_db["payments"].insert_one(payment3.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            # Filter by "john"
            response = client.get(
                "/api/v1/payments/?month=4&year=2024&student_name=john",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_payments"] == 2  # John Doe and John Smith
            assert data["total_amount"] == 300.0  # 100 + 200
    
    def test_monthly_payments_without_month_fails(self, client, mock_db):
        """Test getting payments without month parameter fails"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Missing month
            response = client.get(
                "/api/v1/payments/?year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 422
    
    def test_monthly_payments_without_year_fails(self, client, mock_db):
        """Test getting payments without year parameter fails"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Missing year
            response = client.get(
                "/api/v1/payments/?month=1",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 422
    
    def test_monthly_payments_with_invalid_month_fails(self, client, mock_db):
        """Test getting payments with invalid month fails validation"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Month > 12
            response = client.get(
                "/api/v1/payments/?month=13&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 422
            
            # Month < 1
            response = client.get(
                "/api/v1/payments/?month=0&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 422
    
    def test_monthly_payments_returns_empty_when_none(self, client, mock_db):
        """Test getting payments returns empty list when no payments exist"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/payments/?month=5&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_payments"] == 0
            assert data["total_amount"] == 0.0
            assert len(data["payments"]) == 0
    
    def test_monthly_payments_sorted_by_date_descending(self, client, mock_db):
        """Test payments are returned sorted by date (newest first)"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create payments in random order
        payment1 = Payment(
            student_name="Student 1",
            amount=100.0,
            payment_date=datetime(2024, 6, 5),
            created_by=admin._id
        )
        payment2 = Payment(
            student_name="Student 2",
            amount=200.0,
            payment_date=datetime(2024, 6, 25),  # Latest
            created_by=admin._id
        )
        payment3 = Payment(
            student_name="Student 3",
            amount=150.0,
            payment_date=datetime(2024, 6, 15),
            created_by=admin._id
        )
        
        mock_db["payments"].insert_one(payment1.to_dict())
        mock_db["payments"].insert_one(payment2.to_dict())
        mock_db["payments"].insert_one(payment3.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/payments/?month=6&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            payments = response.json()["payments"]
            
            # First payment should be the latest (June 25)
            assert payments[0]["student_name"] == "Student 2"


class TestPaymentAuthorization:
    """Test payment endpoint access control"""
    
    def test_payment_endpoints_require_authentication(self, client):
        """Test payment endpoints require authentication"""
        # Create payment without token
        response = client.post(
            "/api/v1/payments/",
            json={
                "student_name": "Test",
                "amount": 100.0,
                "payment_date": "2024-01-15T10:00:00"
            }
        )
        assert response.status_code == 403
        
        # Get payments without token
        response = client.get("/api/v1/payments/?month=1&year=2024")
        assert response.status_code == 403
    
    def test_teacher_cannot_access_any_payment_endpoint(self, client, mock_db):
        """Test teacher is blocked from all payment endpoints"""
        teacher = User(
            username="teacher",
            hashed_password=get_password_hash("teacher123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(teacher.to_dict())
        
        token = create_access_token({
            "sub": teacher._id,
            "username": teacher.username,
            "role": teacher.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Try create
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Test",
                    "amount": 100.0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            assert response.status_code == 403
            
            # Try get
            response = client.get(
                "/api/v1/payments/?month=1&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 403


class TestPaymentDecemberEdgeCase:
    """Test December payment handling (edge case)"""
    
    def test_december_payments_dont_include_january(self, client, mock_db):
        """Test December payments don't include January of next year"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create December and January payments
        payment_dec = Payment(
            student_name="Dec Student",
            amount=100.0,
            payment_date=datetime(2024, 12, 25),
            created_by=admin._id
        )
        payment_jan = Payment(
            student_name="Jan Student",
            amount=200.0,
            payment_date=datetime(2025, 1, 5),
            created_by=admin._id
        )
        
        mock_db["payments"].insert_one(payment_dec.to_dict())
        mock_db["payments"].insert_one(payment_jan.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            # Get December 2024
            response = client.get(
                "/api/v1/payments/?month=12&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_payments"] == 1  # Only December
            assert data["payments"][0]["student_name"] == "Dec Student"


class TestPaymentIntegration:
    """Test complete payment workflows"""
    
    def test_create_and_retrieve_payment_flow(self, client, mock_db):
        """Test complete flow: create payment → retrieve in monthly report"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            # 1. Create payment
            create_response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Integration Test",
                    "amount": 500.0,
                    "payment_date": "2024-07-15T10:00:00",
                    "notes": "Integration test payment"
                }
            )
            
            assert create_response.status_code == 201
            payment_data = create_response.json()
            
            # 2. Retrieve payment in monthly report
            get_response = client.get(
                "/api/v1/payments/?month=7&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert get_response.status_code == 200
            monthly_data = get_response.json()
            
            assert monthly_data["total_payments"] == 1
            assert monthly_data["total_amount"] == 500.0
            assert monthly_data["payments"][0]["student_name"] == "Integration Test"
    
    def test_multiple_students_multiple_payments(self, client, mock_db):
        """Test scenario with multiple students making multiple payments"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create multiple payments for different students
        payments_data = [
            ("Student A", 100.0, datetime(2024, 8, 5)),
            ("Student A", 150.0, datetime(2024, 8, 15)),  # Same student, second payment
            ("Student B", 200.0, datetime(2024, 8, 10)),
            ("Student B", 100.0, datetime(2024, 8, 20)),
            ("Student C", 300.0, datetime(2024, 8, 12)),
        ]
        
        for student, amount, date in payments_data:
            payment = Payment(
                student_name=student,
                amount=amount,
                payment_date=date,
                created_by=admin._id
            )
            mock_db["payments"].insert_one(payment.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/payments/?month=8&year=2024",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_payments"] == 5
            assert data["total_amount"] == 850.0  # Sum of all


class TestPaymentEdgeCases:
    """Test payment edge cases and special scenarios"""
    
    def test_payment_with_very_long_student_name(self, client, mock_db):
        """Test payment with maximum length student name"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            long_name = "A" * 100  # Maximum 100 chars
            
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": long_name,
                    "amount": 100.0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            
            assert response.status_code == 201
    
    def test_payment_with_empty_student_name_fails(self, client, mock_db):
        """Test payment with empty student name fails validation"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "",  # Empty
                    "amount": 100.0,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            
            assert response.status_code == 422
    
    def test_payment_with_decimal_precision(self, client, mock_db):
        """Test payment correctly handles decimal amounts"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.payments.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.payments_collection = mock_db["payments"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/payments/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "student_name": "Decimal Test",
                    "amount": 99.99,
                    "payment_date": "2024-01-15T10:00:00"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["amount"] == 99.99

