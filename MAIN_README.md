# General Institute System - Backend

FastAPI backend for managing institute operations: teachers, lessons, and student payments.

## ⚡ Quick Start

```bash
# 1. Create & activate virtual environment
python -m venv venv
    .\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env file
# Edit .env with MongoDB credentials and SECRET_KEY

# 4. Test MongoDB connection
python scripts\databases_scriptis\test_connection.py

# 5. Initialize database
python scripts\databases_scriptis\setup_database.py

# 6. Run server
uvicorn app.main:app --reload
```


## 🧪 Testing

```bash
# Run all tests (user + admin)
pytest

# Run only admin tests
pytest tests/admin/ -v

# Run with coverage
pytest --cov=app --cov-report=html
```
