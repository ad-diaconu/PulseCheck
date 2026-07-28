## [unreleased]

### 🚀 Features

- *(documentation)* Add PRD,HLD,ERD files for business logic comprehension
- *(documentation)* Add rest of business logic  files and assets
- Add initial uv.lock
- *(db)* Implement sqlalchemy database models and pydantic schemas
- *(auth)* Implement core jwt authentication and global exception classes
- *(logging)* Configure centralized applciation logging
- *(frontend)* Add main page
- *(frontend)* Add auth page
- *(auth)* Add frontend protected routes and apply changes
- *(workspace)* Add workspace related routes, schemas, models, exception and integration  test
- *(monitors)* Add monitor routes
- *(api)* Add monitor and ping_history endpoints
- *(ping_history)* Add background tasks via celery and redis
- *(ping_history)* Update celery config and docker setup
- *(app)* Add .gitignore and dev docker compose
- *(ping_history)* Add integration tests and setup testing scripts

### 💼 Other

- Solve password hashing problem by adopting bcrypt over passlib

### 🚜 Refactor

- *(api)* Restructure endpoints into dedicated routers and update main app
- *(app)* Adopt scalable layered app structure

### 📚 Documentation

- Add contributing guidelines and branch naming conventions
- Change CONTRIBUTING.MD formating
- *(backend)* Modify relative path to figure in ERD.md

### 🧪 Testing

- *(core)* Add global pytest fixtures and configuration
- *(auth)* Add unit and integration tests for authentication flow
- *(api)* Add integration tests for protected routes
- *(api)* Test monitor endpoints
- *(api)* Add integration tests for ping_history module
- *(api)* Change test database engine to PostgreSQL
- *(api)* Add automated database setup and pytest run using Makefile

### ⚙️ Miscellaneous Tasks

- *(config)* Update dependencies and add docker compose setup
- *(github)* Add github pr template
