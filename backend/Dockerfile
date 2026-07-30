FROM python:3.12-slim

ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1

# uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# working directory
WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

# copy rest of the project files
COPY . .

RUN uv sync --frozen

CMD ["uvicorn","backend.app.main:app","--host","0.0.0.0","--port","8000"]