FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir requests pandas pyarrow

COPY . /app

CMD ["python", "openf1_ingest.py"]
