.PHONY: setup build up down test clean quality format lint type-check

PYTHON = python
MODULES = {% if cookiecutter.use_process == 'yes' %}process {% endif %}{% if cookiecutter.use_grpc == 'yes' %}grpc {% endif %}{% if cookiecutter.use_rest == 'yes' %}rest {% endif %}{% if cookiecutter.use_mqtt == 'yes' %}mqtt {% endif %}{% if cookiecutter.use_ftp == 'yes' %}ftp {% endif %}{% if cookiecutter.use_webrtc == 'yes' %}webrtc {% endif %}{% if cookiecutter.use_websocket == 'yes' %}websocket {% endif %}{% if cookiecutter.use_imap == 'yes' %}imap {% endif %}{% if cookiecutter.use_smtp == 'yes' %}smtp {% endif %}{% if cookiecutter.use_pop3 == 'yes' %}pop3 {% endif %}{% if cookiecutter.use_ssh == 'yes' %}ssh {% endif %}{% if cookiecutter.use_mcp == 'yes' %}mcp {% endif %}{% if cookiecutter.use_shell == 'yes' %}shell {% endif %}

# Konfiguracja projektu
setup:
	@echo "Konfiguracja projektu..."
	poetry install
	pre-commit install

security:
	@echo "Sprawdzanie bezpieczeństwa kodu..."
	$(PYTHON) -m $(QUALITY_MODULE).security $(MODULES) --config-dir $(CONFIG_DIR)


# Sprawdzanie dokumentacji
doc-check:
	@echo "Sprawdzanie dokumentacji kodu..."
	$(PYTHON) -m lib.quality.custom.doc_checker $(MODULES)


# Zadania związane z jakością kodu
quality: format lint type-check security doc-check test

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