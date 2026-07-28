# 📈 Pulse Check

## 📋 Table of Contents

- [🔎 Overview](#-overview)
- [📂 Folder Structure](#-folder-structure)
- [🛠️ Key Components](#️-key-components)
- [🎯 Use Cases](#-use-cases)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Development Setup](#development-setup)
  - [Running the Full Environment](#running-the-full-environment)
- [🏛️ Architecture](#️-architecture)
- [🧩 Microservices](#-microservices)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

# 🔎 Overview

**Pulse Check** is an uptime monitoring platform offering **per-minute tracking** and **instant alerts** for client websites and APIs. It allows users to manage multiple monitors in organized workspaces while tracking HTTP status codes and response latencies in real time.

---

# 📂 Folder Structure

```text
pulse-check/
├── backend/                  # FastAPI application & Celery workers
│   ├── app/                  # Core API logic, models, schemas, and routes
│   ├── migrations/           # Alembic versioning and migration scripts
│   ├── alembic.ini           # Alembic configuration
│   └── pyproject.toml        # Python dependencies managed by uv
├── frontend/                 # React Single Page Application (SPA)
├── docker-compose.yml        # Infrastructure services (PostgreSQL, Redis)
└── README.md
```

---

# 🛠️ Key Components

### Frontend
- React Single Page Application (SPA)
- Dashboard
- Workspace management
- User authentication

### Backend
- FastAPI REST API
- Authentication (JWT & OAuth2)
- CRUD operations
- Rate limiting

### Database
- PostgreSQL
- SQLAlchemy ORM
- Alembic migrations

### Broker & Cache
- Redis
- Rate limiting
- Session management
- Celery message broker

### Background Tasks
- Celery Worker
- Celery Beat scheduler
- HTTP monitoring jobs

---

# 🎯 Use Cases

## ✅ Core Features

### Authentication
Users can create an account using email and password or sign in using OAuth2 providers such as Google or GitHub.

### Workspaces
Users can create personal workspaces to organize monitors (for example, **Client X Monitoring**) and invite collaborators with different roles such as **Admin** or **Viewer**.

### Monitor Management
Users can:
- Create monitors
- Edit monitors
- Delete monitors
- Pause or resume monitoring

### Data Collection
The system periodically performs HTTP requests against every active monitor (every 1 or 5 minutes), storing:

- HTTP Status Code
- Response Time (Latency)
- Timestamp

### Dashboard
Users can:

- View monitoring history
- Filter by HTTP status code
- Sort by date
- Sort by latency
- Browse results using pagination

---

## 🚫 Out of Scope (Version 1)

- TCP monitoring
- gRPC monitoring
- Database monitoring
- SSH monitoring
- SMS alerts
- Phone call alerts
- Infinite scrolling

Version 1 focuses exclusively on **HTTP/HTTPS monitoring** with **Email** and **Webhook** notifications.

---

# 🚀 Getting Started

Follow these instructions to set up the project locally for development.

---

## Prerequisites

Install the following tools:

- Git
- Docker
- Docker Compose
- uv (Python package manager)
- Node.js
- npm

---

## Environment Configuration

Create your environment variables file.

```bash
# From backend/
cp .env.example .env
```

Configure:

- DATABASE_URL
- Redis connection
- JWT Secret
- OAuth credentials
- Email credentials (optional)

---

## Development Setup

This project uses:

- SQLAlchemy
- Alembic

All migration commands must be executed inside the `backend/` directory.

### Apply migrations

```bash
uv run alembic upgrade head
```

---

### Create a migration

```bash
uv run alembic revision --autogenerate -m "short description"
```

---

### Roll back the latest migration

```bash
uv run alembic downgrade -1
```

---

## Running the Full Environment

Clone the repository:

```bash
git clone <repository-url>
cd pulse-check
```

Create the environment file:

```bash
cp backend/.env.example backend/.env
```

Install Python dependencies:

```bash
cd backend
uv sync
```

Start infrastructure services:

```bash
docker compose up -d
```

Apply database migrations:

```bash
uv run alembic upgrade head
```

Start the backend:

```bash
uv run fastapi dev
```

Start the frontend:

```bash
cd ../frontend
npm install
npm run dev
```

The application is now ready for development.

---

# 🏛️ Architecture

Pulse Check follows an event-driven architecture.

```text
             +----------------------+
             |      React SPA       |
             +----------+-----------+
                        |
                     HTTPS
                        |
                        ▼
              +------------------+
              |    FastAPI API   |
              +------------------+
                 |           |
                 |           |
                 ▼           ▼
          PostgreSQL      Redis
             ▲               ▲
             |               |
             |         Celery Beat
             |               |
             |               ▼
             |        Redis Queue
             |               |
             |               ▼
             |        Celery Worker
             |               |
             +---------------+
                     |
                     ▼
              Client Websites
               HTTP / HTTPS
```

### Request Flow

1. React communicates with the FastAPI API.
2. FastAPI authenticates users via JWT or OAuth2.
3. Configuration data is stored in PostgreSQL.
4. Rate limiting is handled using Redis.
5. Celery Beat schedules monitoring jobs.
6. Redis queues monitoring tasks.
7. Celery Workers execute HTTP requests.
8. Results are saved into PostgreSQL.
9. Alerts are sent when downtime is detected.

---

# 🧩 Microservices

Currently, Pulse Check is deployed as a **modular monolith**.

The FastAPI application contains:

- REST API
- Authentication
- Business logic
- Background task orchestration

The architecture allows Celery Workers and task queues to be extracted into independent microservices as monitoring traffic increases.

---

# 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/AmazingFeature
```

3. Commit your changes.

```bash
git commit -m "Add AmazingFeature"
```

4. Push your branch.

```bash
git push origin feature/AmazingFeature
```

5. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

See the `LICENSE` file for details.