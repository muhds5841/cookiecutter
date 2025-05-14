"""Implementacja adaptacyjnego próbkowania dla LLM."""

from collections import deque
import time
import random
from typing import Dict, Any, List, Optional, Deque
import numpy as np


class SamplingStats:
    """Statystyki próbkowania dla adaptacyjnego algorytmu."""

    def __init__(self, latency: float = 0.0, tokens: int = 0, success: bool = True):
        """
        Inicjalizuje statystyki próbkowania.

        Args:
            latency: Czas odpowiedzi (ms)
            tokens: Liczba tokenów wygenerowanych
            success: Czy próbkowanie zakończyło się sukcesem
        """
        self.latency = latency
        self.tokens = tokens
        self.success = success
        self.timestamp = time.time()


class AdaptiveSampler:
    """
    Adaptacyjny sampler dla LLM.
    Dostosowuje parametry próbkowania w oparciu o historyczne wyniki.
    """

    def __init__(self, history_size: int = 100):
        """
        Inicjalizuje adaptacyjny sampler.

        Args:
            history_size: Rozmiar historii próbkowania
        """
        self.history: Deque[SamplingStats] = deque(maxlen=history_size)
        self.min_temperature = 0.1
        self.max_temperature = 1.2
        self.min_top_p = 0.1
        self.max_top_p = 1.0
        self.base_temperature = 0.7
        self.base_top_p = 0.9

    def add_sampling_result(self, stats: SamplingStats):
        """
        Dodaje wynik próbkowania do historii.

        Args:
            stats: Statystyki próbkowania
        """
        self.history.append(stats)

    def get_sampling_params(self) -> Dict[str, Any]:
        """
        Oblicza optymalne parametry próbkowania na podstawie historii.

        Returns:
            Parametry próbkowania dla LLM
        """
        if not self.history:
            # Brak historii, użyj parametrów bazowych
            return {
                "temperature": self.base_temperature,
                "top_p": self.base_top_p
            }

        # Obliczenie średnich wartości z historii
        recent_history = list(self.history)[-20:]  # Ostatnie 20 próbek
        avg_latency = np.mean([h.latency for h in recent_history]) if recent_history else 0
        success_rate = np.mean([float(h.success) for h in recent_history]) if recent_history else 1.0

        # Dostosowanie parametrów na podstawie wyników
        temperature = self.base_temperature
        top_p = self.base_top_p

        # Jeśli latencja jest wysoka, zmniejsz temperaturę
        if avg_latency > 1000:  # > 1s
            temperature = max(self.min_temperature, self.base_temperature - 0.2)
        elif avg_latency < 200:  # < 200ms
            temperature = min(self.max_temperature, self.base_temperature + 0.1)

        # Jeśli współczynnik powodzenia jest niski, zwiększ top_p
        if success_rate < 0.8:
            top_p = min(self.max_top_p, self.base_top_p + 0.1)
        elif success_rate > 0.95:
            top_p = max(self.min_top_p, self.base_top_p - 0.05)

        return {
            "temperature": round(temperature, 2),
            "top_p": round(top_p, 2)
        }


class SamplingManager:
    """
    Manager próbkowania dla LLM.
    Zarządza różnymi strategiami próbkowania i wybiera najlepszą.
    """

    def __init__(self):
        """Inicjalizuje manager próbkowania."""
        self.samplers = {
            "adaptive": AdaptiveSampler(),
            "conservative": AdaptiveSampler(),
            "creative": AdaptiveSampler()
        }

        # Konfiguracja dla różnych profili
        self.samplers["conservative"].base_temperature = 0.3
        self.samplers["conservative"].base_top_p = 0.8

        self.samplers["creative"].base_temperature = 1.0
        self.samplers["creative"].base_top_p = 1.0

    def get_sampling_params(self, profile: str = "adaptive") -> Dict[str, Any]:
        """
        Zwraca parametry próbkowania dla podanego profilu.

        Args:
            profile: Profil próbkowania (adaptive, conservative, creative)

        Returns:
            Parametry próbkowania
        """
        if profile not in self.samplers:
            profile = "adaptive"

        return self.samplers[profile].get_sampling_params()

    def record_sampling_result(
            self,
            profile: str,
            latency: float,
            tokens: int,
            success: bool
    ):
        """
        Zapisuje wynik próbkowania dla podanego profilu.

        Args:
            profile: Profil próbkowania
            latency: Czas odpowiedzi (ms)
            tokens: Liczba tokenów
            success: Czy próbkowanie zakończyło się sukcesem
        """
        if profile in self.samplers:
            stats = SamplingStats(latency, tokens, success)
            self.samplers[profile].add_sampling_result(stats)