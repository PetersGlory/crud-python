# 🚀 crud-python (FastAPI)

A **FastAPI-based CRUD API** implementing Create, Read, Update, and Delete operations with authentication and PostgreSQL.
This project serves as a clean starter template for building production-ready RESTful APIs using **FastAPI**.

---

## ✨ Features

- ⚡ FastAPI (high-performance async API)
- 🧱 Clean CRUD architecture
- 🔐 JWT authentication
- 🐘 PostgreSQL database
- 📦 Pydantic schemas for validation
- 🔁 SQLAlchemy ORM
- 🐳 Docker & Docker Compose support
- 📖 Automatic Swagger & ReDoc documentation

---

## 🗂️ Project Structure

```text
crud-python/
├── .env.example
├── auth.py              # Authentication logic (JWT)
├── database.py          # DB connection & session
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── main.py              # FastAPI app entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🧠 Prerequisites

- Python **3.9+**
- pip
- PostgreSQL
- Docker & Docker Compose (optional)

---

## ⚙️ Local Development Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/PetersGlory/crud-python.git
cd crud-python
```

---

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv .venv
```

```bash
# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Update `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=crud_db
JWT_SECRET=your-secret-key
```

---

## 🐘 Database Setup

Create the database manually:

```sql
CREATE DATABASE crud_db;
```

Ensure PostgreSQL is running before starting the API.

---

## ▶️ Run FastAPI Application

```bash
uvicorn main:app --reload
```

API runs at:

```
http://localhost:8000
```

---

## 📘 API Documentation (FastAPI Built‑in)

FastAPI automatically generates interactive API docs:

- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc

---

## 🐳 Docker Setup (Recommended)

### Build & Run Containers

```bash
docker compose up --build
```

Services started:
- FastAPI application
- PostgreSQL database

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|------|--------|------------|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login & receive JWT |

### Users
| Method | Endpoint | Description |
|------|--------|------------|
| GET | `/users` | Get all users |
| GET | `/users/{id}` | Get user by ID |
| POST | `/users` | Create user |
| PUT | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |

---

## 🔐 Authentication Usage

1. Login via `/auth/login`
2. Copy the JWT token
3. Add to request headers:

```http
Authorization: Bearer <YOUR_TOKEN>
```

---

## 🧪 Sample Request

```bash
curl -X POST http://localhost:8000/users \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "username": "john",
  "email": "john@example.com",
  "password": "secret"
}'
```

---

## 🛑 Stop Containers

```bash
docker compose down -v
```

---

## 🤝 Contributing

Contributions are welcome.
Open an issue or submit a pull request.

---

## 📄 License

MIT License © PetersGlory
