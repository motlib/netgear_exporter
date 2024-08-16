FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip pipenv \
    && adduser -h /app -H -u 4242 -D appuser

ADD Pipfile Pipfile.lock /app/

RUN pipenv install --deploy --extra-pip-args "--no-cache-dir" --system

ADD . /app/

# API will listen on this port
EXPOSE 8177

USER appuser

# Start API server
ENTRYPOINT ["python", "-m", "netgear_exporter"]
