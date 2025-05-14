from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from process.process import ProcessEngine


class VoiceResource:
    def __init__(self, config):
        self.process = ProcessEngine(config)

    def get_available_voices(self, language: str = None) -> List[Dict[str, Any]]:
        """
        Pobiera listę dostępnych głosów

        Args:
            language: Opcjonalny filtr języka

        Returns:
            Lista dostępnych głosów z metadanymi
        """
        voices = self.process.get_available_voices()

        if language:
            voices = [v for v in voices if v.get('language') == language]

        return voices