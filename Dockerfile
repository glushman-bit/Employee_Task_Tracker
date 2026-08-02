FROM python:3.14-slim

LABEL authors="Ivan"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry==1.8.0 \
    && poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
