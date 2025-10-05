# Base image
FROM python:3.12-slim
LABEL org.opencontainers.image.title="applicativo-backend" \
      org.opencontainers.image.description="IA Applicativo Backend" \
      org.opencontainers.image.source="https://github.com/${GITHUB_REPOSITORY}" \
      org.opencontainers.image.revision="${GITHUB_SHA}" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
# Diretório de trabalho
WORKDIR /raiz

# System deps (keep minimal; add others only if you really need them)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential gcc \
 && rm -rf /var/lib/apt/lists/*

 # install dependencies
COPY [ "requirements.txt", "docker-entrypoint.sh", "./"]
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt && chmod +x ./docker-entrypoint.sh

# copy project
COPY . .

RUN chmod +x /raiz/docker-entrypoint.sh

# Expõe porta da API (UVicorn) e da Flower, se desejar
EXPOSE 8000 5555

# Entry point
ENTRYPOINT ["/raiz/docker-entrypoint.sh"]

# Processo padrão (substituível no docker-compose)
CMD ["/raiz/docker-entrypoint.sh", "api"]