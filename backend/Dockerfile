FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Capa de dependencias separada del código para aprovechar la cache de Docker.
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY . .

EXPOSE 8300

# --port fija el puerto del contenedor aunque config.toml diga otro, para que coincida con EXPOSE y docker-compose.yml.
CMD ["uv", "run", "app.py", "--host", "0.0.0.0", "--port", "8300"]
