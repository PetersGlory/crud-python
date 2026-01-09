# 📦 crud-python

**CRUD Python API** — A simple and extensible Python backend that implements Create, Read, Update, and Delete (CRUD) operations.  
Designed as a learning project and a solid starter template for RESTful backend services.

---

## 🚀 Features

- RESTful API with full CRUD functionality
- JWT-based authentication
- PostgreSQL database integration
- Environment-based configuration
- Docker & Docker Compose support
- Clean, modular project structure

---

## 📁 Project Structure

```text
crud-python/
├── .env.example
├── auth.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🧠 Prerequisites

Make sure you have the following installed:

- Python 3.9+
- pip
- PostgreSQL (for local setup)
- Docker & Docker Compose (optional but recommended)

---

## ⚙️ Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/PetersGlory/crud-python.git
cd crud-python
```

---

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env` with your database and secret values:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=crud_db
JWT_SECRET=your-secret-key
```

---

## 🐘 Database Setup

Create the PostgreSQL database:

```sql
CREATE DATABASE crud_db;
```

Ensure PostgreSQL is running before starting the app.

---

## ▶️ Run the Application

```bash
python main.py
```

The API will be available at:

```
http://localhost:8000
```

---

## 🚢 Docker Setup (Recommended)

This project includes Docker support for easy setup.

### Build and Run Containers

```bash
docker compose up --build
```

This will start:
- PostgreSQL database container
- Python API container

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|------|--------|------------|
| GET | `/users` | Fetch all users |
| GET | `/users/{id}` | Fetch user by ID |
| POST | `/users` | Create a new user |
| PUT | `/users/{id}` | Update a user |
| DELETE | `/users/{id}` | Delete a user |
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login and receive JWT |

---

## 🔐 Authentication

The API uses JWT for authentication.

1. Login via `/auth/login`
2. Receive a token
3. Use it in requests:

```
Authorization: Bearer <TOKEN>
```

---

## 🧪 Example Request

### Create User

```bash
curl -X POST http://localhost:8000/users \
-H "Content-Type: application/json" \
-d '{"username":"john","email":"john@example.com","password":"secret"}'
```

---

## 🧹 Stop & Clean Docker Containers

```bash
docker compose down -v
```

---

## 🤝 Contributing

Pull requests and issues are welcome.  
Feel free to fork and improve the project.

---

## 📄 License

This project is licensed under the MIT License.
