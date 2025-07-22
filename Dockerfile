FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

WORKDIR /app

COPY ./app /app/

COPY ./mcp.json /app/
COPY ./api_keys.json /app/
COPY ./uv.lock /app/
COPY ./pyproject.toml /app/

RUN uv sync

CMD [ "uv", "run", "-m", "main" ]
