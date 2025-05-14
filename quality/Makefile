.PHONY: setup build up down test clean quality format lint type-check

# Domyślne środowisko
ENV ?= dev

# Konfiguracja projektu
setup:
	@echo "Konfiguracja projektu..."
	pre-commit install
	cd process && $(MAKE) setup
	cd grpc && $(MAKE) setup
	cd rest && $(MAKE) setup
	cd webrtc && $(MAKE) setup
	cd mcp && $(MAKE) setup
	cd shell && $(MAKE) setup

# Zadania związane z jakością kodu
quality: format lint type-check

# Formatowanie kodu
format:
	@echo "Formatowanie kodu..."
	black .
	isort .

# Sprawdzanie stylu kodu
lint:
	@echo "Sprawdzanie stylu kodu..."
	flake8 .
	pylint process grpc rest webrtc mcp shell

# Sprawdzanie typów
type-check:
	@echo "Sprawdzanie typów..."
	mypy .

# Testy z Tox
tox:
	@echo "Uruchamianie testów w wielu środowiskach..."
	tox

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

# Uruchamianie testów
test:
	@echo "Uruchamianie testów..."
	pytest

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