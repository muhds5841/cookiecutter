.PHONY: setup build up down test clean quality format lint type-check

PYTHON = python
MODULES = {% if cookiecutter.components.tts_engine %}tts_engine {% endif %}{% if cookiecutter.components.grpc %}grpc {% endif %}{% if cookiecutter.components.rest %}rest {% endif %}{% if cookiecutter.components.webrtc %}webrtc {% endif %}{% if cookiecutter.components.mcp %}mcp {% endif %}{% if cookiecutter.components.shell %}shell {% endif %}

# Konfiguracja projektu
setup:
	@echo "Konfiguracja projektu..."
	poetry install
	pre-commit install

# Zadania związane z jakością kodu
quality: format-check lint type-check test

# Formatowanie kodu
format:
	@echo "Formatowanie kodu..."
	poetry run black .
	poetry run isort .

# Sprawdzanie formatowania kodu
format-check:
	@echo "Sprawdzanie formatowania kodu..."
	poetry run black --check .
	poetry run isort --check .

# Sprawdzanie stylu kodu
lint:
	@echo "Sprawdzanie stylu kodu..."
	poetry run flake8 $(MODULES)

# Sprawdzanie typów
type-check:
	@echo "Sprawdzanie typów..."
	poetry run mypy $(MODULES)

# Uruchamianie testów
test:
	@echo "Uruchamianie testów..."
	poetry run pytest --cov=$(MODULES) tests/

# Czyszczenie projektu
clean:
	@echo "Czyszczenie projektu..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

{% if cookiecutter.use_docker == "yes" %}
# Budowanie kontenerów
build:
	@echo "Budowanie kontenerów Docker..."
	docker-compose build

# Uruchamianie wszystkich serwisów
up:
	@echo "Uruchamianie serwisów..."
	docker-compose up -d

# Zatrzymywanie serwisów
down:
	@echo "Zatrzymywanie serwisów..."
	docker-compose down
{% endif %}