FROM python:{{ cookiecutter.python_version }}-slim

WORKDIR /app

COPY ../tts_engine/pyproject.toml .
COPY ../tts_engine .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

CMD ["python", "-m", "process"]