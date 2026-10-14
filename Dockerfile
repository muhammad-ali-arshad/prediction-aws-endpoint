FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 appuser

COPY api.py .
USER appuser
EXPOSE 5500

CMD ["gunicorn", "--bind", "0.0.0.0:5500", "--workers", "2", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "api:app"]
