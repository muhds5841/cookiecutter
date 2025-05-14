"""Generyczny proces - przykład integracji z konfiguracją i logowaniem."""

from lib.config import get_config
from lib.logging import get_logger

class Process:
    """Bazowa klasa procesu."""

    @staticmethod
    def get_parameters_schema():
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Dane wejściowe dla procesu"
                }
            },
            "required": ["input"]
        }

    @staticmethod
    def get_returns_schema():
        return {
            "type": "object",
            "properties": {
                "output": {
                    "type": "string",
                    "description": "Wynik procesu"
                }
            }
        }

    def run(self, parameters):
        logger = get_logger()
        config = get_config()
        logger.info(f"Uruchamianie procesu z parametrami: {parameters}")
        # Przykładowa logika procesu
        output = parameters["input"].upper()
        logger.info(f"Wynik procesu: {output}")
        return {"output": output}

class DefaultProcess(Process):
    """Przykładowa domyślna implementacja procesu."""
    pass
