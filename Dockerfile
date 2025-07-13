FROM python:3.11-slim

ENV PATH="/src/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /src/
COPY ./src pyproject.toml uv.lock ./

RUN uv sync --locked

CMD ["python3.11", "/src/main.py"]