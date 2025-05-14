"""
Moduł zawierający narzędzia do monitorowania i health check dla usług Process.
"""

import os
import sys
import json
import time
import threading
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from http.server import HTTPServer, BaseHTTPRequestHandler

from core.logging import get_logger


class MetricsCollector:
    """Kolektor metryk dla usług Process."""
    
    def __init__(self, service_name: str, metrics_port: int = 9090):
        """Inicjalizuje kolektor metryk.
        
        Args:
            service_name: Nazwa usługi
            metrics_port: Port dla serwera metryk
        """
        self.service_name = service_name
        self.metrics_port = metrics_port
        self.logger = get_logger(f"{service_name}.metrics")
        
        # Słowniki metryk
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        
        # Blokada dla bezpiecznego dostępu do metryk
        self.lock = threading.Lock()
        
        # Uruchom serwer HTTP dla metryk
        self.start_server()
        
        self.logger.info(f"Kolektor metryk zainicjalizowany dla usługi {service_name} na porcie {metrics_port}")
    
    def register_counter(self, name: str, description: str):
        """Rejestruje licznik.
        
        Args:
            name: Nazwa licznika
            description: Opis licznika
        """
        with self.lock:
            self.counters[name] = {
                "value": 0,
                "description": description
            }
    
    def register_gauge(self, name: str, description: str):
        """Rejestruje wskaźnik.
        
        Args:
            name: Nazwa wskaźnika
            description: Opis wskaźnika
        """
        with self.lock:
            self.gauges[name] = {
                "value": 0,
                "description": description
            }
    
    def register_histogram(self, name: str, description: str, buckets: List[float] = None):
        """Rejestruje histogram.
        
        Args:
            name: Nazwa histogramu
            description: Opis histogramu
            buckets: Lista progów histogramu
        """
        if buckets is None:
            buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        
        with self.lock:
            self.histograms[name] = {
                "sum": 0,
                "count": 0,
                "buckets": {str(b): 0 for b in buckets},
                "description": description
            }
    
    def increment(self, name: str, value: float = 1):
        """Inkrementuje licznik.
        
        Args:
            name: Nazwa licznika
            value: Wartość do dodania
        """
        with self.lock:
            if name in self.counters:
                self.counters[name]["value"] += value
    
    def set(self, name: str, value: float):
        """Ustawia wartość wskaźnika.
        
        Args:
            name: Nazwa wskaźnika
            value: Wartość do ustawienia
        """
        with self.lock:
            if name in self.gauges:
                self.gauges[name]["value"] = value
    
    def observe(self, name: str, value: float):
        """Dodaje obserwację do histogramu.
        
        Args:
            name: Nazwa histogramu
            value: Wartość obserwacji
        """
        with self.lock:
            if name in self.histograms:
                histogram = self.histograms[name]
                histogram["sum"] += value
                histogram["count"] += 1
                
                # Aktualizuj kubełki
                for bucket in sorted([float(b) for b in histogram["buckets"].keys()]):
                    if value <= bucket:
                        histogram["buckets"][str(bucket)] += 1
    
    def get_metrics(self) -> str:
        """Zwraca metryki w formacie Prometheus.
        
        Returns:
            Metryki w formacie Prometheus
        """
        with self.lock:
            lines = []
            
            # Dodaj liczniki
            for name, counter in self.counters.items():
                lines.append(f"# HELP {name} {counter['description']}")
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {counter['value']}")
                lines.append("")
            
            # Dodaj wskaźniki
            for name, gauge in self.gauges.items():
                lines.append(f"# HELP {name} {gauge['description']}")
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {gauge['value']}")
                lines.append("")
            
            # Dodaj histogramy
            for name, histogram in self.histograms.items():
                lines.append(f"# HELP {name} {histogram['description']}")
                lines.append(f"# TYPE {name} histogram")
                
                # Dodaj kubełki
                for bucket, count in histogram["buckets"].items():
                    bucket_line = f"{name}_bucket" + "{{le=\"" + str(bucket) + "\"}} " + str(count)
                    lines.append(bucket_line)
                
                # Dodaj sumę i liczbę
                lines.append(f"{name}_sum {histogram['sum']}")
                lines.append(f"{name}_count {histogram['count']}")
                lines.append("")
            
            return "\n".join(lines)
    
    def start_server(self):
        """Uruchamia serwer HTTP dla metryk."""
        class MetricsHandler(BaseHTTPRequestHandler):
            def __init__(self_handler, *args, **kwargs):
                self_handler.metrics_collector = self
                super().__init__(*args, **kwargs)
            
            def do_GET(self_handler):
                if self_handler.path == "/metrics":
                    metrics_data = self.get_metrics()
                    self_handler.send_response(200)
                    self_handler.send_header("Content-type", "text/plain")
                    self_handler.end_headers()
                    self_handler.wfile.write(metrics_data.encode())
                else:
                    self_handler.send_response(404)
                    self_handler.send_header("Content-type", "text/plain")
                    self_handler.end_headers()
                    self_handler.wfile.write(b"Not Found")
            
            def log_message(self_handler, format, *args):
                # Przekieruj logi do naszego loggera
                self.logger.debug(format % args)
        
        def run_server():
            server = HTTPServer(("0.0.0.0", self.metrics_port), MetricsHandler)
            self.logger.info(f"Serwer metryk uruchomiony na porcie {self.metrics_port}")
            server.serve_forever()
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()


class HealthCheck:
    """Klasa do sprawdzania stanu zdrowia usług Process."""
    
    def __init__(self, service_name: str, check_interval: int = 30, timeout: int = 5):
        """Inicjalizuje health check.
        
        Args:
            service_name: Nazwa usługi
            check_interval: Interwał sprawdzania w sekundach
            timeout: Timeout dla sprawdzeń w sekundach
        """
        self.service_name = service_name
        self.check_interval = check_interval
        self.timeout = timeout
        self.logger = get_logger(f"{service_name}.health")
        
        # Słownik funkcji sprawdzających
        self.checks = {}
        
        # Słownik wyników sprawdzeń
        self.results = {
            "service": service_name,
            "timestamp": time.time(),
            "status": "unknown",
            "checks": {}
        }
        
        # Blokada dla bezpiecznego dostępu do wyników
        self.lock = threading.Lock()
        
        # Uruchom wątek sprawdzający
        self.start_check_thread()
        
        self.logger.info(f"Health check zainicjalizowany dla usługi {service_name}")
    
    def register_check(self, name: str, check_func: Callable[[], Dict[str, Any]]):
        """Rejestruje funkcję sprawdzającą.
        
        Args:
            name: Nazwa sprawdzenia
            check_func: Funkcja sprawdzająca, która zwraca słownik ze statusem
        """
        with self.lock:
            self.checks[name] = check_func
            self.results["checks"][name] = {
                "status": "unknown",
                "timestamp": time.time(),
                "details": {}
            }
    
    def run_checks(self):
        """Uruchamia wszystkie zarejestrowane sprawdzenia."""
        with self.lock:
            self.results["timestamp"] = time.time()
            
            all_healthy = True
            
            for name, check_func in self.checks.items():
                try:
                    # Uruchom sprawdzenie z timeoutem
                    result = self._run_with_timeout(check_func, self.timeout)
                    
                    # Aktualizuj wyniki
                    self.results["checks"][name] = {
                        "status": result.get("status", "unknown"),
                        "timestamp": time.time(),
                        "details": result.get("details", {})
                    }
                    
                    # Sprawdź, czy wszystkie sprawdzenia są zdrowe
                    if result.get("status") != "healthy":
                        all_healthy = False
                
                except Exception as e:
                    self.logger.error(f"Błąd podczas sprawdzania {name}: {str(e)}")
                    self.results["checks"][name] = {
                        "status": "unhealthy",
                        "timestamp": time.time(),
                        "details": {"error": str(e)}
                    }
                    all_healthy = False
            
            # Aktualizuj ogólny status
            self.results["status"] = "healthy" if all_healthy else "unhealthy"
    
    def _run_with_timeout(self, func: Callable, timeout: int) -> Dict[str, Any]:
        """Uruchamia funkcję z timeoutem.
        
        Args:
            func: Funkcja do uruchomienia
            timeout: Timeout w sekundach
        
        Returns:
            Wynik funkcji lub słownik z błędem, jeśli wystąpił timeout
        """
        result = {"status": "unhealthy", "details": {"error": "Timeout"}}
        
        def target():
            nonlocal result
            try:
                result = func()
            except Exception as e:
                result = {"status": "unhealthy", "details": {"error": str(e)}}
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            return {"status": "unhealthy", "details": {"error": "Timeout"}}
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca aktualny status zdrowia.
        
        Returns:
            Słownik ze statusem zdrowia
        """
        with self.lock:
            return dict(self.results)
    
    def start_check_thread(self):
        """Uruchamia wątek sprawdzający."""
        def run_checks():
            while True:
                try:
                    self.run_checks()
                except Exception as e:
                    self.logger.error(f"Błąd podczas uruchamiania sprawdzeń: {str(e)}")
                
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=run_checks, daemon=True)
        thread.start()


def create_health_endpoint(service_name: str, health_check: HealthCheck, port: int = 8080):
    """Tworzy endpoint HTTP dla health check.
    
    Args:
        service_name: Nazwa usługi
        health_check: Obiekt HealthCheck
        port: Port dla serwera HTTP
    
    Returns:
        Wątek serwera HTTP
    """
    logger = get_logger(f"{service_name}.health.endpoint")
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health" or self.path == "/healthz":
                health_status = health_check.get_status()
                
                # Ustal kod odpowiedzi na podstawie statusu
                response_code = 200 if health_status["status"] == "healthy" else 503
                
                self.send_response(response_code)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(health_status).encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Not Found")
        
        def log_message(self, format, *args):
            # Przekieruj logi do naszego loggera
            logger.debug(format % args)
    
    def run_server():
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        logger.info(f"Serwer health check uruchomiony na porcie {port}")
        server.serve_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread
