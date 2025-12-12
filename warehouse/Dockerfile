FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir dbt-duckdb

COPY . /app

# For now, keep the container running so dbt commands can be executed manually.
CMD ["bash", "-c", "tail -f /dev/null"]

