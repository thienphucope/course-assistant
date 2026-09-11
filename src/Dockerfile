# Self-contained runtime template. Build with:
# docker build -t course-assistant src
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENTRYPOINT ["python", "run.py", "--root", "/app"]
CMD ["--help"]
