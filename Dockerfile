FROM python:3.12-slim

WORKDIR /app

#RUN apt-get update \
#    && BUILD_DEPS="" \
#    && apt-get install -y ${BUILD_DEPS} \
#    && pip install --upgrade pip pipenv

RUN pip install --upgrade pip pipenv

ADD Pipfile Pipfile.lock /app/

RUN pipenv install --system

# Create a group and user to run the app
#ARG APP_USER=appuser
#RUN mkdir -p /app /app/data \
#        && adduser --home /app --no-create-home --uid 4242 ${APP_USER}
RUN adduser --home /app --no-create-home --uid 4242 appuser

# Install packages needed to run the application
#RUN apt-get update \
#    && RUN_DEPS="" \
#    && apt-get install -y ${RUN_DEPS} \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD . /app/
#COPY --from=buildenv /app/.venv /app/.venv

# API will listen on this port
EXPOSE 8000

USER appuser

# Start API server
CMD ["python", "-m", "netgear_exporter"]
