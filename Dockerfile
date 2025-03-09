FROM python:3.11-slim-buster

WORKDIR /usr/src/app/src

COPY ./pyproject.toml ./

COPY . .

RUN pip install --upgrade pip
RUN pip install -e .

CMD ["poetry", "run", "hueta-bot"]
