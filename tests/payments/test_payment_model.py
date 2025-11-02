"""
Comprehensive tests for Payment model
Tests: Business logic, data conversion, database operations
"""
import pytest
from datetime import datetime, timedelta
from app.models.payment import Payment


class TestPaymentModelCreation:
    """Test Payment model instantiation"""
    
    def test_create_payment_with_required_fields(self):
        """Test creating payment with only required fields"""
        payment = Payment(
            student_name="John Doe",
            amount=100.50,
            payment_date=datetime(2024, 1, 15),
            created_by="admin-id"
        )
        
        assert payment.student_name == "John Doe"
        assert payment.amount == 100.50
        assert payment.payment_date == datetime(2024, 1, 15)
        assert payment.created_by == "admin-id"
        assert payment._id is not None  # Auto-generated UUID
        assert payment.created_at is not None
        assert payment.student_email is None
        assert payment.lesson_id is None
        assert payment.notes is None
    
    def test_create_payment_with_all_fields(self):
        """Test creating payment with all fields"""
        now = datetime.utcnow()
        payment = Payment(
            student_name="Jane Smith",
            student_email="jane@example.com",
            amount=250.75,
            payment_date=datetime(2024, 2, 20),
            lesson_id="lesson-123",
            notes="First installment",
            created_by="admin-xyz",
            _id="custom-payment-id",
            created_at=now
        )
        
        assert payment.student_name == "Jane Smith"
        assert payment.student_email == "jane@example.com"
        assert payment.amount == 250.75
        assert payment.lesson_id == "lesson-123"
        assert payment.notes == "First installment"
        assert payment.created_by == "admin-xyz"
        assert payment._id == "custom-payment-id"
        assert payment.created_at == now
    
    def test_payment_id_auto_generation(self):
        """Test that payment ID is auto-generated if not provided"""
        payment1 = Payment(
            student_name="Student 1",
            amount=100.0,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        payment2 = Payment(
            student_name="Student 2",
            amount=200.0,
            payment_date=datetime(2024, 1, 2),
            created_by="admin"
        )
        
        assert payment1._id is not None
        assert payment2._id is not None
        assert payment1._id != payment2._id  # Each payment gets unique ID


class TestPaymentBusinessLogic:
    """Test Payment model business logic methods"""
    
    def test_is_recent_returns_true_for_recent_payment(self):
        """Test is_recent() for payment within last 30 days"""
        recent_date = datetime.utcnow() - timedelta(days=10)
        payment = Payment(
            student_name="Test",
            amount=100.0,
            payment_date=recent_date,
            created_by="admin"
        )
        
        assert payment.is_recent(days=30) is True
    
    def test_is_recent_returns_false_for_old_payment(self):
        """Test is_recent() for payment older than specified days"""
        old_date = datetime.utcnow() - timedelta(days=100)
        payment = Payment(
            student_name="Test",
            amount=100.0,
            payment_date=old_date,
            created_by="admin"
        )
        
        assert payment.is_recent(days=30) is False
    
    def test_is_recent_with_custom_days(self):
        """Test is_recent() with custom day threshold"""
        payment_date = datetime.utcnow() - timedelta(days=5)
        payment = Payment(
            student_name="Test",
            amount=100.0,
            payment_date=payment_date,
            created_by="admin"
        )
        
        assert payment.is_recent(days=7) is True
        assert payment.is_recent(days=3) is False
    
    def test_get_month_returns_correct_month(self):
        """Test get_month() returns payment month"""
        payment = Payment(
            student_name="Test",
            amount=100.0,
            payment_date=datetime(2024, 5, 15),
            created_by="admin"
        )
        
        assert payment.get_month() == 5
    
    def test_get_year_returns_correct_year(self):
        """Test get_year() returns payment year"""
        payment = Payment(
            student_name="Test",
            amount=100.0,
            payment_date=datetime(2024, 5, 15),
            created_by="admin"
        )
        
        assert payment.get_year() == 2024


class TestPaymentDataConversion:
    """Test Payment model data conversion methods"""
    
    def test_to_dict_converts_all_fields(self):
        """Test to_dict() includes all payment fields"""
        payment = Payment(
            student_name="Test Student",
            student_email="student@test.com",
            amount=150.50,
            payment_date=datetime(2024, 3, 10),
            lesson_id="lesson-123",
            notes="Test payment",
            created_by="admin-id"
        )
        
        data = payment.to_dict()
        
        assert data["_id"] == payment._id
        assert data["student_name"] == "Test Student"
        assert data["student_email"] == "student@test.com"
        assert data["amount"] == 150.50
        assert data["payment_date"] == datetime(2024, 3, 10)
        assert data["lesson_id"] == "lesson-123"
        assert data["notes"] == "Test payment"
        assert data["created_by"] == "admin-id"
        assert "created_at" in data
    
    def test_to_dict_handles_optional_fields(self):
        """Test to_dict() handles None values correctly"""
        payment = Payment(
            student_name="Student",
            amount=100.0,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        
        data = payment.to_dict()
        
        assert data["student_email"] is None
        assert data["lesson_id"] is None
        assert data["notes"] is None
    
    def test_from_dict_creates_payment_from_database_doc(self):
        """Test from_dict() recreates Payment from database document"""
        doc = {
            "_id": "payment-123",
            "student_name": "John Doe",
            "student_email": "john@example.com",
            "amount": 200.0,
            "payment_date": datetime(2024, 1, 15),
            "lesson_id": "lesson-456",
            "notes": "Monthly payment",
            "created_by": "admin-789",
            "created_at": datetime(2024, 1, 10)
        }
        
        payment = Payment.from_dict(doc)
        
        assert payment._id == "payment-123"
        assert payment.student_name == "John Doe"
        assert payment.student_email == "john@example.com"
        assert payment.amount == 200.0
        assert payment.payment_date == datetime(2024, 1, 15)
        assert payment.lesson_id == "lesson-456"
        assert payment.notes == "Monthly payment"
        assert payment.created_by == "admin-789"
    
    def test_from_dict_handles_missing_optional_fields(self):
        """Test from_dict() with minimal document"""
        doc = {
            "student_name": "Minimal",
            "amount": 50.0,
            "payment_date": datetime(2024, 1, 1),
            "created_by": "admin"
        }
        
        payment = Payment.from_dict(doc)
        
        assert payment.student_name == "Minimal"
        assert payment.amount == 50.0
        assert payment.student_email is None
        assert payment.lesson_id is None
    
    def test_roundtrip_conversion(self):
        """Test Payment -> dict -> Payment maintains data"""
        original = Payment(
            student_name="Roundtrip Test",
            student_email="roundtrip@test.com",
            amount=300.0,
            payment_date=datetime(2024, 6, 1),
            lesson_id="lesson-rt",
            notes="Roundtrip test",
            created_by="admin-rt"
        )
        
        data = original.to_dict()
        recreated = Payment.from_dict(data)
        
        assert recreated.student_name == original.student_name
        assert recreated.student_email == original.student_email
        assert recreated.amount == original.amount
        assert recreated.payment_date == original.payment_date
        assert recreated.lesson_id == original.lesson_id
        assert recreated.notes == original.notes


class TestPaymentDatabaseMethods:
    """Test Payment model database interaction methods"""
    
    def test_find_by_id_returns_payment_when_exists(self, mock_db):
        """Test find_by_id() finds existing payment"""
        payment = Payment(
            student_name="Test",
            amount=100.0,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        mock_db["payments"].insert_one(payment.to_dict())
        
        found = Payment.find_by_id(payment._id, mock_db["payments"])
        
        assert found is not None
        assert found._id == payment._id
        assert found.student_name == "Test"
    
    def test_find_by_id_returns_none_when_not_exists(self, mock_db):
        """Test find_by_id() returns None for non-existent payment"""
        found = Payment.find_by_id("nonexistent-id", mock_db["payments"])
        assert found is None
    
    def test_find_by_student_name_returns_matching_payments(self, mock_db):
        """Test find_by_student_name() finds payments by name (case-insensitive)"""
        payment1 = Payment(
            student_name="John Doe",
            amount=100.0,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        payment2 = Payment(
            student_name="john smith",
            amount=200.0,
            payment_date=datetime(2024, 1, 2),
            created_by="admin"
        )
        payment3 = Payment(
            student_name="Jane Doe",
            amount=150.0,
            payment_date=datetime(2024, 1, 3),
            created_by="admin"
        )
        
        mock_db["payments"].insert_one(payment1.to_dict())
        mock_db["payments"].insert_one(payment2.to_dict())
        mock_db["payments"].insert_one(payment3.to_dict())
        
        # Search for "john" (case-insensitive)
        found = Payment.find_by_student_name("john", mock_db["payments"])
        
        assert len(found) == 2  # john doe and john smith
        names = [p.student_name.lower() for p in found]
        assert all("john" in name for name in names)
    
    def test_find_by_student_name_returns_empty_when_none(self, mock_db):
        """Test find_by_student_name() returns empty list when no matches"""
        found = Payment.find_by_student_name("nonexistent", mock_db["payments"])
        assert len(found) == 0
    
    def test_find_by_month_returns_payments_in_month(self, mock_db):
        """Test find_by_month() returns all payments in specific month"""
        # Create payments in different months
        payment_jan = Payment(
            student_name="Jan Student",
            amount=100.0,
            payment_date=datetime(2024, 1, 15),
            created_by="admin"
        )
        payment_feb = Payment(
            student_name="Feb Student",
            amount=200.0,
            payment_date=datetime(2024, 2, 15),
            created_by="admin"
        )
        payment_jan2 = Payment(
            student_name="Jan Student 2",
            amount=150.0,
            payment_date=datetime(2024, 1, 25),
            created_by="admin"
        )
        
        mock_db["payments"].insert_one(payment_jan.to_dict())
        mock_db["payments"].insert_one(payment_feb.to_dict())
        mock_db["payments"].insert_one(payment_jan2.to_dict())
        
        # Find January payments
        jan_payments = Payment.find_by_month(1, 2024, mock_db["payments"])
        
        assert len(jan_payments) == 2
        assert all(p.get_month() == 1 for p in jan_payments)
        assert all(p.get_year() == 2024 for p in jan_payments)
    
    def test_find_by_month_returns_empty_when_none(self, mock_db):
        """Test find_by_month() returns empty list when no payments"""
        found = Payment.find_by_month(5, 2024, mock_db["payments"])
        assert len(found) == 0
    
    def test_find_by_month_handles_december(self, mock_db):
        """Test find_by_month() correctly handles December"""
        payment_dec = Payment(
            student_name="Dec Student",
            amount=100.0,
            payment_date=datetime(2024, 12, 25),
            created_by="admin"
        )
        payment_jan = Payment(
            student_name="Jan Student",
            amount=200.0,
            payment_date=datetime(2025, 1, 5),
            created_by="admin"
        )
        
        mock_db["payments"].insert_one(payment_dec.to_dict())
        mock_db["payments"].insert_one(payment_jan.to_dict())
        
        # Find December payments
        dec_payments = Payment.find_by_month(12, 2024, mock_db["payments"])
        
        assert len(dec_payments) == 1
        assert dec_payments[0].get_month() == 12
    
    def test_find_by_lesson_id_returns_matching_payments(self, mock_db):
        """Test find_by_lesson_id() finds all payments for a lesson"""
        lesson_id = "lesson-456"
        
        payment1 = Payment(
            student_name="Student 1",
            amount=100.0,
            payment_date=datetime(2024, 1, 1),
            lesson_id=lesson_id,
            created_by="admin"
        )
        payment2 = Payment(
            student_name="Student 2",
            amount=200.0,
            payment_date=datetime(2024, 1, 2),
            lesson_id=lesson_id,
            created_by="admin"
        )
        payment3 = Payment(
            student_name="Student 3",
            amount=150.0,
            payment_date=datetime(2024, 1, 3),
            lesson_id="other-lesson",
            created_by="admin"
        )
        
        mock_db["payments"].insert_one(payment1.to_dict())
        mock_db["payments"].insert_one(payment2.to_dict())
        mock_db["payments"].insert_one(payment3.to_dict())
        
        found = Payment.find_by_lesson_id(lesson_id, mock_db["payments"])
        
        assert len(found) == 2
        assert all(p.lesson_id == lesson_id for p in found)
    
    def test_calculate_total_sums_payment_amounts(self):
        """Test calculate_total() sums all payment amounts"""
        payment1 = Payment(
            student_name="S1",
            amount=100.50,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        payment2 = Payment(
            student_name="S2",
            amount=250.75,
            payment_date=datetime(2024, 1, 2),
            created_by="admin"
        )
        payment3 = Payment(
            student_name="S3",
            amount=50.25,
            payment_date=datetime(2024, 1, 3),
            created_by="admin"
        )
        
        payments = [payment1, payment2, payment3]
        total = Payment.calculate_total(payments)
        
        assert total == 401.50  # 100.50 + 250.75 + 50.25
    
    def test_calculate_total_returns_zero_for_empty_list(self):
        """Test calculate_total() returns 0 for empty list"""
        total = Payment.calculate_total([])
        assert total == 0.0
    
    def test_calculate_total_rounds_to_two_decimals(self):
        """Test calculate_total() rounds to 2 decimal places"""
        payment1 = Payment(
            student_name="S1",
            amount=10.333,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        payment2 = Payment(
            student_name="S2",
            amount=20.667,
            payment_date=datetime(2024, 1, 2),
            created_by="admin"
        )
        
        total = Payment.calculate_total([payment1, payment2])
        
        assert total == 31.0  # Rounded
    
    def test_save_inserts_payment_into_database(self, mock_db):
        """Test save() inserts payment document into database"""
        payment = Payment(
            student_name="Save Test",
            amount=500.0,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        
        # Database should be empty
        assert mock_db["payments"].count_documents({}) == 0
        
        # Save payment
        payment.save(mock_db["payments"])
        
        # Payment should be in database
        assert mock_db["payments"].count_documents({}) == 1
        found = mock_db["payments"].find_one({"student_name": "Save Test"})
        assert found is not None
        assert found["amount"] == 500.0
    
    def test_delete_removes_payment_from_database(self, mock_db):
        """Test delete() removes payment from database"""
        payment = Payment(
            student_name="Delete Test",
            amount=100.0,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        mock_db["payments"].insert_one(payment.to_dict())
        
        # Payment exists
        assert mock_db["payments"].count_documents({"_id": payment._id}) == 1
        
        # Delete payment
        payment.delete(mock_db["payments"])
        
        # Payment should be removed
        assert mock_db["payments"].count_documents({"_id": payment._id}) == 0


class TestPaymentRepr:
    """Test Payment model string representation"""
    
    def test_repr_shows_payment_info(self):
        """Test __repr__() shows payment ID, student, and amount"""
        payment = Payment(
            student_name="Test Student",
            amount=123.45,
            payment_date=datetime(2024, 1, 1),
            created_by="admin",
            _id="payment-789"
        )
        
        repr_str = repr(payment)
        
        assert "payment-789" in repr_str
        assert "Test Student" in repr_str
        assert "123.45" in repr_str


class TestPaymentAmountHandling:
    """Test payment amount validation and handling"""
    
    def test_payment_preserves_decimal_precision(self):
        """Test payment amounts maintain decimal precision"""
        payment = Payment(
            student_name="Decimal Test",
            amount=99.99,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        
        assert payment.amount == 99.99
        
        data = payment.to_dict()
        assert data["amount"] == 99.99
        
        recreated = Payment.from_dict(data)
        assert recreated.amount == 99.99
    
    def test_payment_handles_large_amounts(self):
        """Test payment can handle large amounts"""
        payment = Payment(
            student_name="Big Spender",
            amount=9999999.99,
            payment_date=datetime(2024, 1, 1),
            created_by="admin"
        )
        
        assert payment.amount == 9999999.99

