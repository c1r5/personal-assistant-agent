FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV NODE_VERSION=20

WORKDIR /app

RUN apt-get update && \
  apt-get install -y curl gpg ca-certificates && \
  mkdir -p /etc/apt/keyrings && \
  curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
  echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_VERSION.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
  apt-get update && \
  apt-get install -y nodejs && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*


COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

COPY ./pyproject.toml ./uv.lock /app/

RUN uv sync

COPY ./app /app/
COPY ./mcp.json /app/
COPY ./api_keys.json /app/

CMD ["uv", "run", "-m", "main"]

