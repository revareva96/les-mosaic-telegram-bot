FROM python:3.12-slim

ENV PATH="/src/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /src/
COPY ./alembic ./alembic
COPY ./src pyproject.toml uv.lock alembic.ini entrypoint.sh ./

RUN uv sync --locked

ENTRYPOINT ["bash", "-c", "source /src/entrypoint.sh && \"$@\"", "--"]
CMD ["python3.12", "/src/main.py"]