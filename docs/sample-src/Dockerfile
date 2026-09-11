FROM python:3.12-slim

LABEL org.opencontainers.image.title="CO3085 Course Assistant"
LABEL org.opencontainers.image.description="Classical grammar-driven NLP sample project"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8

WORKDIR /app

COPY pyproject.toml README.md requirements.txt ./
COPY src ./src
COPY conf ./conf
COPY data ./data
COPY input ./input
COPY models ./models
COPY run.py ./run.py

RUN python -m compileall -q src && mkdir -p /app/output

CMD ["python", "run.py", "all", "--samples", "1000"]
