# Stage to export requirements.txt from poetry
FROM python:3.12-alpine as poetry

RUN pip install --no-cache-dir poetry poetry-plugin-export

ADD pyproject.toml poetry.lock /

RUN poetry export --format requirements.txt > requirements.txt


FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=poetry requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && adduser -h /app -H -u 4242 -D appuser

ADD . /app/

# API will listen on this port
EXPOSE 8177

USER appuser

# Start API server
ENTRYPOINT ["python", "-m", "netgear_exporter"]
