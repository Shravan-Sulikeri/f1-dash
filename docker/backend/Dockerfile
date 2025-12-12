FROM python:3.11-slim

WORKDIR /opt/backend

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /opt/backend/requirements.txt
RUN pip install --no-cache-dir -r /opt/backend/requirements.txt

COPY backend/app /opt/backend/app

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
