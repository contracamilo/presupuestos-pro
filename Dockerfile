FROM python:3.12-slim

# Librerías del sistema que necesita WeasyPrint y una fuente con tildes, «ñ» y €
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi8 shared-mime-info \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY presupuestos ./presupuestos
COPY tests ./tests
RUN pip install --no-cache-dir ".[dev]"

RUN useradd --create-home --uid 1000 app \
    && mkdir -p /datos /copias \
    && chown app:app /datos /copias
USER app

# Una sola instancia: SQLite (research.md D15)
CMD ["uvicorn", "presupuestos.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
