FROM python:3.11-slim

COPY requirements.txt /
RUN python -m venv /.venv && /.venv/bin/pip install -r /requirements.txt && mkdir /app
WORKDIR /app
ADD pyproject.toml ./
COPY . ./
RUN /.venv/bin/pip install -e /app

CMD ["/.venv/bin/hueta-bot"]
