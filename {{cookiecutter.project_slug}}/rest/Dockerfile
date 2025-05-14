FROM python:{{ cookiecutter.python_version }}-slim

WORKDIR /app

COPY pyproject.toml .
COPY . .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

EXPOSE 5000

CMD ["python", "server.py"]
