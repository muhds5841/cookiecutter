.PHONY: setup build up down test clean quality format lint type-check

PYTHON = python
QUALITY_MODULE = lib.quality
MODULES = process grpc rest webrtc mcp shell
CONFIG_DIR = quality

# Domyślne środowisko
ENV ?= dev

# Konfiguracja projektu
setup:
	@echo "Konfiguracja projektu..."
	$(PYTHON) -m $(QUALITY_MODULE).hooks setup
	$(MAKE) install-deps

# Instalacja zależności
install-deps:
	@echo "Instalacja zależności..."
	poetry install
	for module in $(MODULES); do \
		cd $$module && poetry install && cd ..; \
	done

# Zadania związane z jakością kodu
quality: format lint type-check test

# Formatowanie kodu
format:
	@echo "Formatowanie kodu..."
	$(PYTHON) -m $(QUALITY_MODULE).formatters . --config $(CONFIG_DIR)/pyproject.toml

# Sprawdzanie czy kod jest poprawnie sformatowany
format-check:
	@echo "Sprawdzanie formatowania kodu..."
	$(PYTHON) -m $(QUALITY_MODULE).formatters . --check --config $(CONFIG_DIR)/pyproject.toml

# Sprawdzanie stylu kodu
lint:
	@echo "Sprawdzanie stylu kodu..."
	$(PYTHON) -m $(QUALITY_MODULE).linters $(MODULES) --config-dir $(CONFIG_DIR)

# Sprawdzanie typów
type-check:
	@echo "Sprawdzanie typów..."
	mypy --config-file $(CONFIG_DIR)/pyproject.toml $(MODULES)

# Testy z pytest
test:
	@echo "Uruchamianie testów..."
	$(PYTHON) -m $(QUALITY_MODULE).testers --test-type pytest --config-dir $(CONFIG_DIR)

# Testy z tox
tox:
	@echo "Uruchamianie testów w wielu środowiskach..."
	$(PYTHON) -m $(QUALITY_MODULE).testers --test-type tox --config-dir $(CONFIG_DIR)

# Raport jakości kodu
report:
	@echo "Generowanie raportu jakości kodu..."
	$(PYTHON) -m $(QUALITY_MODULE).reporters --output-dir reports

# Budowanie kontenerów
build: quality
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

# Czyszczenie projektu
clean:
	@echo "Czyszczenie projektu..."
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name "reports" -exec rm -rf {} +