FROM python:3.10.13-slim-bookworm as builder
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 -
WORKDIR /usr/src/dormyboba
COPY dormyboba ./
COPY pyproject.toml poetry.lock ./
RUN export POETRY=${HOME}/.local/bin/poetry && \
    ${POETRY} config virtualenvs.in-project true && \
    ${POETRY} install
FROM python:3.10.13-slim-bookworm
WORKDIR /app
ENV CONFIG_DIR "/config"
COPY --from=builder /usr/src/dormyboba/ ./
CMD ["/app/.venv/bin/python3", "-m", "dormyboba"]
