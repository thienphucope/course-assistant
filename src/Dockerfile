# Runtime template. Build from the repository root:
# docker build -f src/Dockerfile -t course-assistant .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY src/requirements.txt /app/src/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/src/requirements.txt

COPY src /app/src
COPY data /app/data
WORKDIR /app/src

ENTRYPOINT ["python", "run.py", "--root", "/app"]
CMD ["--help"]
