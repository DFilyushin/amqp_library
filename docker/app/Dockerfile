FROM python:3.9

ARG CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apt update \
    && apt install -y gcc musl-dev libffi-dev openssl make ncat \
    && pip install --no-cache-dir poetry

COPY . /var/project
COPY ./docker/app/start.sh /var/project/start.sh

WORKDIR /var/project

RUN python -m venv /var/project/env \
    && . /var/project/env/bin/activate \
    && poetry install \
    && apt clean -y \
    && chmod +x /var/project/start.sh

CMD /var/project/start.sh
