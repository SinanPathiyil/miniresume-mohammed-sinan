# Mini Resume Collector API

A production-ready FastAPI application for managing candidate resumes with comprehensive validation, error handling, and API documentation.

## 📋 Overview

This REST API allows you to upload, store, and manage candidate resumes with metadata. Built with clean architecture principles, it features modular design, comprehensive error handling, structured logging, and full API documentation.

## 🚀 Features

- **Resume Upload**: Upload candidate resumes (PDF, DOC, DOCX) with metadata
- **Advanced Filtering**: Search candidates by skills, experience, and graduation year
- **Data Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Detailed error messages with proper HTTP status codes
- **Logging**: Structured logging for monitoring and debugging
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Thread-Safe Storage**: In-memory storage with concurrent access support
- **Clean Architecture**: Modular design with separation of concerns

## 🛠️ Technology Stack

- **Python**: 3.10
- **Framework**: FastAPI 0.109.0
- **Validation**: Pydantic 2.5.3
- **Server**: Uvicorn 0.27.0
- **File Handling**: Python Multipart

## 📁 Project Structure

```
mini-resume-collector/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── storage.py       # In-memory storage
│   │   └── candidate.py     # Business logic
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py        # Health check
│   │   └── candidates.py    # Candidate CRUD
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py        # Logging setup
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── file_handler.py  # File operations
│   └── middleware/
│       ├── __init__.py
│       └── error_handler.py # Global error handling
├── uploads/                  # Resume files (auto-created)
├── logs/                     # Application logs (auto-created)
├── requirements.txt
├── README.md
└── .gitignore
```

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/miniresume-your-name.git
   cd miniresume-your-name
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running the Application

### Development Mode

```bash
# Method 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
Check if the API is running.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-15T20:46:55",
  "version": "1.0.0",
  "message": "Service is running"
}
```

---

#### 2. Upload Resume
Upload a new candidate resume with metadata.

**Request:**
```http
POST /candidates
Content-Type: multipart/form-data
```

**Form Data:**
- `full_name` (string, required): Candidate's full name
- `dob` (string, required): Date of birth (YYYY-MM-DD)
- `contact_number` (string, required): Phone number (10-12 digits)
- `contact_address` (string, required): Full address
- `education_qualification` (string, required): Highest education
- `graduation_year` (integer, required): Year of graduation (1950-2030)
- `years_of_experience` (float, required): Years of experience (0-50)
- `skill_set` (string, required): Comma-separated skills
- `resume` (file, required): Resume file (PDF/DOC/DOCX, max 10MB)

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/candidates" \
  -F "full_name=John Doe" \
  -F "dob=1995-06-15" \
  -F "contact_number=9876543210" \
  -F "contact_address=123 Main Street, City, State, PIN-123456" \
  -F "education_qualification=B.Tech in Computer Science" \
  -F "graduation_year=2020" \
  -F "years_of_experience=3.5" \
  -F "skill_set=Python, FastAPI, Docker, PostgreSQL" \
  -F "resume=@/path/to/resume.pdf"
```

**Response (201 Created):**
```json
{
  "id": 1,
  "full_name": "John Doe",
  "dob": "1995-06-15",
  "contact_number": "9876543210",
  "contact_address": "123 Main Street, City, State, PIN-123456",
  "education_qualification": "B.Tech in Computer Science",
  "graduation_year": 2020,
  "years_of_experience": 3.5,
  "skill_set": ["Python", "FastAPI", "Docker", "PostgreSQL"],
  "resume_filename": "abc123def456.pdf",
  "created_at": "2026-02-15T20:46:55"
}
```

---

#### 3. List Candidates
Retrieve all candidates with optional filters.

**Request:**
```http
GET /candidates?skill={skill}&min_experience={min}&max_experience={max}&graduation_year={year}
```

**Query Parameters (all optional):**
- `skill` (string): Filter by skill (case-insensitive)
- `min_experience` (float): Minimum years of experience
- `max_experience` (float): Maximum years of experience
- `graduation_year` (integer): Filter by graduation year

**Examples:**
```bash
# Get all candidates
curl "http://localhost:8000/candidates"

# Filter by skill
curl "http://localhost:8000/candidates?skill=Python"

# Filter by experience range
curl "http://localhost:8000/candidates?min_experience=2&max_experience=5"

# Filter by graduation year
curl "http://localhost:8000/candidates?graduation_year=2020"

# Combine filters
curl "http://localhost:8000/candidates?skill=Python&min_experience=3"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "full_name": "John Doe",
    "dob": "1995-06-15",
    "contact_number": "9876543210",
    "contact_address": "123 Main Street, City, State, PIN-123456",
    "education_qualification": "B.Tech in Computer Science",
    "graduation_year": 2020,
    "years_of_experience": 3.5,
    "skill_set": ["Python", "FastAPI", "Docker", "PostgreSQL"],
    "resume_filename": "abc123.pdf",
    "created_at": "2026-02-15T20:46:55"
  }
]
```

---

#### 4. Get Candidate by ID
Retrieve a specific candidate's details.

**Request:**
```http
GET /candidates/{candidate_id}
```

**Example:**
```bash
curl "http://localhost:8000/candidates/1"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "full_name": "John Doe",
  "dob": "1995-06-15",
  "contact_number": "9876543210",
  "contact_address": "123 Main Street, City, State, PIN-123456",
  "education_qualification": "B.Tech in Computer Science",
  "graduation_year": 2020,
  "years_of_experience": 3.5,
  "skill_set": ["Python", "FastAPI", "Docker", "PostgreSQL"],
  "resume_filename": "abc123.pdf",
  "created_at": "2026-02-15T20:46:55"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "CandidateNotFound",
  "message": "Candidate with ID 999 not found",
  "timestamp": "2026-02-15T20:46:55"
}
```

---

#### 5. Delete Candidate
Delete a candidate and their resume file.

**Request:**
```http
DELETE /candidates/{candidate_id}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/candidates/1"
```

**Response (200 OK):**
```json
{
  "message": "Candidate 1 deleted successfully",
  "deleted_candidate": {
    "id": 1,
    "full_name": "John Doe"
  }
}
```

---











## 🔍 Error Handling

All errors follow a consistent format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "detail": "Optional detailed information",
  "timestamp": "2026-02-15T20:46:55"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input or validation error
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds limit
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Server error

### Example Error Responses

**Validation Error:**
```json
{
  "error": "ValidationError",
  "message": "Request validation failed",
  "detail": [
    {
      "field": "body -> dob",
      "message": "Date of birth must be in YYYY-MM-DD format",
      "type": "value_error"
    }
  ],
  "timestamp": "2026-02-15T20:46:55"
}
```

**Invalid File Type:**
```json
{
  "error": "InvalidFileType",
  "message": "Invalid file type for 'resume.txt'",
  "detail": "Allowed types: .pdf, .doc, .docx",
  "timestamp": "2026-02-15T20:46:55"
}
```

## 📊 Logging

Logs are stored in the `logs/` directory with the following structure:

- `app_YYYYMMDD.log`: All application logs
- `error_YYYYMMDD.log`: Error logs only

Log format:
```
2026-02-15 20:46:55 | app.routes.candidates | INFO | upload_resume:123 | Resume uploaded successfully: ID=1, Name=John Doe
```

## 🧪 Testing with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Health Check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 2. Upload Resume
files = {'resume': open('resume.pdf', 'rb')}
data = {
    'full_name': 'John Doe',
    'dob': '1995-06-15',
    'contact_number': '9876543210',
    'contact_address': '123 Main Street, City, State, PIN-123456',
    'education_qualification': 'B.Tech in Computer Science',
    'graduation_year': 2020,
    'years_of_experience': 3.5,
    'skill_set': 'Python, FastAPI, Docker, PostgreSQL'
}
response = requests.post(f"{BASE_URL}/candidates", files=files, data=data)
print(response.json())
candidate_id = response.json()['id']

# 3. List All Candidates
response = requests.get(f"{BASE_URL}/candidates")
print(response.json())

# 4. Filter by Skill
response = requests.get(f"{BASE_URL}/candidates?skill=Python")
print(response.json())

# 5. Get Candidate by ID
response = requests.get(f"{BASE_URL}/candidates/{candidate_id}")
print(response.json())

# 6. Delete Candidate
response = requests.delete(f"{BASE_URL}/candidates/{candidate_id}")
print(response.json())
```

## 🔒 File Upload Security

- **File Type Validation**: Only PDF, DOC, and DOCX files are accepted
- **File Size Limit**: Maximum 10 MB per file
- **Unique Naming**: Files are renamed using UUID to prevent conflicts
- **Secure Storage**: Files are stored outside the web root

## 🏗️ Architecture Highlights

### Clean Architecture
- **Separation of Concerns**: Routes → Services → Storage
- **Dependency Injection**: Services injected into routes
- **Single Responsibility**: Each module has one clear purpose

### Thread Safety
- **Thread-safe Storage**: In-memory storage with locking mechanisms
- **Concurrent Access**: Safe handling of simultaneous requests
- **Atomic Operations**: ID generation with thread safety

### Error Handling Strategy
- **Global Exception Handler**: Catches all unhandled exceptions
- **Custom Exceptions**: Specific exceptions for business logic
- **Validation Errors**: Detailed field-level error messages
- **Consistent Format**: All errors follow the same structure

## 📝 Configuration

You can customize settings by creating a `.env` file in the project root:

```env
APP_NAME=Mini Resume Collector API
APP_VERSION=1.0.0
DEBUG=False
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
LOG_DIR=logs
LOG_LEVEL=INFO
```

## 🤝 Contributing

This project follows best practices for REST API development:

1. **Meaningful Commits**: Use descriptive commit messages
2. **Code Quality**: Follow PEP 8 style guidelines
3. **Documentation**: Keep API documentation up to date
4. **Error Handling**: Handle all edge cases gracefully
5. **Logging**: Add appropriate logging for debugging

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

Created as part of the Mini Resume Collector assignment for backend development evaluation.

## 🙏 Acknowledgments

- FastAPI framework for excellent API development experience
- Pydantic for robust data validation
- Uvicorn for high-performance ASGI server

---

**Need Help?**

- Visit the interactive API documentation at `/docs` when the server is running
- Check the logs in the `logs/` directory for debugging
- Ensure all dependencies are installed correctly
- Verify Python version is 3.10 or higher
