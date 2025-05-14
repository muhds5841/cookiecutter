# Przykłady implementacji multiprotokołowego wsparcia

Ten dokument zawiera przykłady implementacji multiprotokołowego wsparcia z wykorzystaniem szablonu cookiecutter, gdzie LLM może być procesem przetwarzającym dane z różnych źródeł.

## Spis treści

- [Wprowadzenie](#wprowadzenie)
- [LLM jako proces](#llm-jako-proces)
- [Integracja protokołów](#integracja-protokołów)
- [Testowanie i monitorowanie](#testowanie-i-monitorowanie)
- [Przykłady implementacji](#przykłady-implementacji)

## Wprowadzenie

Szablon cookiecutter umożliwia tworzenie rozwiązań z multiprotokołowym wsparciem, gdzie LLM może być procesem przetwarzającym dane. Dzięki modularnej architekturze, możliwe jest łączenie różnych protokołów (MQTT, REST, gRPC, IMAP, SMTP, SSH, FTP) i wykorzystanie ich jako źródeł danych dla LLM.

## LLM jako proces

Aby wykorzystać LLM jako proces przetwarzający dane, należy zaimplementować klasę dziedziczącą po `ProcessBase` i zarejestrować ją w systemie wtyczek.

### Przykład implementacji LLM jako procesu

```python
# process/llm_process.py
from process.process_base import ProcessBase
from process.plugin_system import register_plugin
import openai
import os

class LLMProcess(ProcessBase):
    """Proces wykorzystujący LLM do przetwarzania tekstu."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        openai.api_key = self.api_key
    
    def process_text(self, text, **options):
        """Przetwarza tekst za pomocą LLM.
        
        Args:
            text: Tekst do przetworzenia
            **options: Dodatkowe opcje przetwarzania
        
        Returns:
            Wynik przetwarzania
        """
        self.logger.info(f"Przetwarzanie tekstu przez LLM: {text[:50]}...")
        
        # Przygotuj parametry dla LLM
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", 500)
        system_prompt = options.get("system_prompt", "Jesteś pomocnym asystentem.")
        
        # Wywołaj LLM
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Przygotuj wynik
        result = self.create_result(
            data=response.choices[0].message.content,
            format="text",
            metadata={
                "model": self.model,
                "usage": response.usage.to_dict(),
                "finish_reason": response.choices[0].finish_reason
            }
        )
        
        return result
    
    def get_resources(self):
        """Zwraca dostępne zasoby.
        
        Returns:
            Lista dostępnych zasobów
        """
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Model GPT-3.5 Turbo od OpenAI"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Model GPT-4 od OpenAI"
            }
        ]

# Zarejestruj plugin
register_plugin("llm", LLMProcess)
```

## Integracja protokołów

Szablon cookiecutter umożliwia integrację różnych protokołów jako źródeł danych dla LLM. Poniżej znajdują się przykłady implementacji.

### Przykład integracji IMAP i LLM

```python
# examples/imap_llm_integration.py
from imap.client import IMAPClient
from process.process import Process
import os

def process_emails_with_llm():
    # Inicjalizacja klienta IMAP
    imap_client = IMAPClient(
        host=os.environ.get("IMAP_HOST", "localhost"),
        port=int(os.environ.get("IMAP_PORT", "143")),
        username=os.environ.get("IMAP_USERNAME", "user"),
        password=os.environ.get("IMAP_PASSWORD", "password")
    )
    
    # Inicjalizacja procesu LLM
    process = Process(plugin="llm")
    
    # Pobierz nieprzeczytane wiadomości
    messages = imap_client.get_messages(criteria="UNSEEN", limit=10)
    
    for message in messages:
        # Przetwórz treść wiadomości przez LLM
        result = process.process_text(
            message["body"],
            system_prompt="Jesteś asystentem, który odpowiada na e-maile. Bądź pomocny i zwięzły.",
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"Wiadomość: {message['subject']}")
        print(f"Odpowiedź LLM: {result.data}")
        print("-" * 50)
        
        # Oznacz wiadomość jako przeczytaną
        imap_client.mark_as_read(message["id"])

if __name__ == "__main__":
    process_emails_with_llm()
```

### Przykład integracji FTP, SSH i LLM

```python
# examples/ftp_ssh_llm_integration.py
from ftp.client import FTPClient
from ssh.client import SSHClient
from process.process import Process
import os
import tempfile

def process_documents_with_llm():
    # Inicjalizacja klientów
    ftp_client = FTPClient(
        host=os.environ.get("FTP_HOST", "localhost"),
        port=int(os.environ.get("FTP_PORT", "21")),
        username=os.environ.get("FTP_USERNAME", "user"),
        password=os.environ.get("FTP_PASSWORD", "password")
    )
    
    ssh_client = SSHClient(
        host=os.environ.get("SSH_HOST", "localhost"),
        port=int(os.environ.get("SSH_PORT", "22")),
        username=os.environ.get("SSH_USERNAME", "user"),
        password=os.environ.get("SSH_PASSWORD", "password")
    )
    
    # Inicjalizacja procesu LLM
    process = Process(plugin="llm")
    
    # Pobierz listę plików z FTP
    files = ftp_client.list_files("/documents")
    text_files = [f for f in files if f["name"].endswith(".txt")]
    
    for file in text_files:
        # Utwórz tymczasowy plik
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
            temp_path = temp.name
        
        # Pobierz plik z FTP
        ftp_client.download_file(file["path"], temp_path)
        
        # Odczytaj zawartość pliku
        with open(temp_path, "r") as f:
            content = f.read()
        
        # Przetwórz zawartość przez LLM
        result = process.process_text(
            content,
            system_prompt="Jesteś asystentem, który analizuje dokumenty. Wyciągnij kluczowe informacje.",
            temperature=0.3,
            max_tokens=1000
        )
        
        # Zapisz wynik do nowego pliku
        summary_path = temp_path + ".summary"
        with open(summary_path, "w") as f:
            f.write(result.data)
        
        # Prześlij wynik na serwer przez SSH
        remote_path = f"/processed/{file['name']}.summary"
        ssh_client.upload_file(summary_path, remote_path)
        
        print(f"Przetworzono plik: {file['name']}")
        print(f"Podsumowanie zapisano na serwerze: {remote_path}")
        print("-" * 50)
        
        # Usuń tymczasowe pliki
        os.unlink(temp_path)
        os.unlink(summary_path)

if __name__ == "__main__":
    process_documents_with_llm()
```

## Testowanie i monitorowanie

Szablon cookiecutter zawiera rozwiązania do testowania i monitorowania usług. Każdy protokół ma zaimplementowane endpointy health check i metryki.

### Endpointy health check

Każda usługa udostępnia endpoint `/health` lub `/healthz`, który zwraca status zdrowia usługi w formacie JSON:

```json
{
  "service": "imap",
  "timestamp": 1621234567.89,
  "status": "healthy",
  "checks": {
    "imap_server": {
      "status": "healthy",
      "timestamp": 1621234567.89,
      "details": {
        "active_connections": 2,
        "server": "0.0.0.0:143"
      }
    },
    "process_connection": {
      "status": "healthy",
      "timestamp": 1621234567.89,
      "details": {
        "resources_count": 2,
        "process_service": "available"
      }
    }
  }
}
```

### Metryki Prometheus

Każda usługa udostępnia endpoint `/metrics`, który zwraca metryki w formacie Prometheus:

```
# HELP imap_connections_total Total number of IMAP connections
# TYPE imap_connections_total counter
imap_connections_total 42

# HELP imap_active_connections Number of active IMAP connections
# TYPE imap_active_connections gauge
imap_active_connections 5

# HELP imap_command_processing_time Time to process IMAP commands
# TYPE imap_command_processing_time histogram
imap_command_processing_time_bucket{le="0.005"} 10
imap_command_processing_time_bucket{le="0.01"} 25
imap_command_processing_time_bucket{le="0.025"} 35
imap_command_processing_time_bucket{le="0.05"} 45
imap_command_processing_time_bucket{le="0.1"} 50
imap_command_processing_time_bucket{le="0.25"} 55
imap_command_processing_time_bucket{le="0.5"} 60
imap_command_processing_time_bucket{le="1"} 65
imap_command_processing_time_bucket{le="2.5"} 70
imap_command_processing_time_bucket{le="5"} 75
imap_command_processing_time_bucket{le="10"} 80
imap_command_processing_time_sum 12.34
imap_command_processing_time_count 80
```

### Przykład testowania API

```python
# tests/test_imap_api.py
import unittest
import requests
import json
import os

class TestIMAPAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = f"http://{os.environ.get('IMAP_HOST', 'localhost')}:{os.environ.get('IMAP_HEALTH_PORT', '8080')}"
    
    def test_health_endpoint(self):
        """Test endpointu health."""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("service", data)
        self.assertEqual(data["service"], "imap")
        self.assertIn("status", data)
        self.assertIn(data["status"], ["healthy", "unhealthy"])
    
    def test_metrics_endpoint(self):
        """Test endpointu metrics."""
        response = requests.get(f"{self.base_url}/metrics")
        self.assertEqual(response.status_code, 200)
        
        metrics = response.text
        self.assertIn("imap_connections_total", metrics)
        self.assertIn("imap_active_connections", metrics)

if __name__ == "__main__":
    unittest.main()
```

## Przykłady implementacji

Poniżej znajdują się przykłady implementacji różnych scenariuszy z wykorzystaniem multiprotokołowego wsparcia.

### Asystent e-mail z LLM

```python
# examples/email_assistant.py
from imap.client import IMAPClient
from smtp.client import SMTPClient
from process.process import Process
import os
import time

def run_email_assistant():
    # Inicjalizacja klientów
    imap_client = IMAPClient(
        host=os.environ.get("IMAP_HOST", "localhost"),
        port=int(os.environ.get("IMAP_PORT", "143")),
        username=os.environ.get("IMAP_USERNAME", "user"),
        password=os.environ.get("IMAP_PASSWORD", "password")
    )
    
    smtp_client = SMTPClient(
        host=os.environ.get("SMTP_HOST", "localhost"),
        port=int(os.environ.get("SMTP_PORT", "25")),
        username=os.environ.get("SMTP_USERNAME", "user"),
        password=os.environ.get("SMTP_PASSWORD", "password")
    )
    
    # Inicjalizacja procesu LLM
    process = Process(plugin="llm")
    
    print("Uruchomiono asystenta e-mail. Naciśnij Ctrl+C, aby zakończyć.")
    
    try:
        while True:
            # Pobierz nieprzeczytane wiadomości
            messages = imap_client.get_messages(criteria="UNSEEN", limit=5)
            
            for message in messages:
                print(f"Przetwarzanie wiadomości: {message['subject']}")
                
                # Przetwórz treść wiadomości przez LLM
                result = process.process_text(
                    message["body"],
                    system_prompt="Jesteś asystentem e-mail. Odpowiedz na pytanie lub prośbę w e-mailu.",
                    temperature=0.7,
                    max_tokens=500
                )
                
                # Wyślij odpowiedź
                smtp_client.send_message(
                    to=message["from"],
                    subject=f"Re: {message['subject']}",
                    body=result.data
                )
                
                print(f"Wysłano odpowiedź do: {message['from']}")
                
                # Oznacz wiadomość jako przeczytaną
                imap_client.mark_as_read(message["id"])
            
            # Czekaj przed kolejnym sprawdzeniem
            time.sleep(60)
    
    except KeyboardInterrupt:
        print("Zakończono działanie asystenta e-mail.")

if __name__ == "__main__":
    run_email_assistant()
```

### System monitorowania z alertami przez MQTT

```python
# examples/monitoring_alerts.py
from mqtt.client import ProcessClient
from ssh.client import SSHClient
from process.process import Process
import os
import time
import json

def run_monitoring_system():
    # Inicjalizacja klientów
    mqtt_client = ProcessClient(
        broker_host=os.environ.get("MQTT_HOST", "localhost"),
        broker_port=int(os.environ.get("MQTT_PORT", "1883"))
    )
    
    ssh_client = SSHClient(
        host=os.environ.get("SSH_HOST", "localhost"),
        port=int(os.environ.get("SSH_PORT", "22")),
        username=os.environ.get("SSH_USERNAME", "user"),
        password=os.environ.get("SSH_PASSWORD", "password")
    )
    
    # Inicjalizacja procesu LLM
    process = Process(plugin="llm")
    
    print("Uruchomiono system monitorowania. Naciśnij Ctrl+C, aby zakończyć.")
    
    try:
        while True:
            # Wykonaj polecenia monitorujące na serwerze
            commands = [
                "df -h | grep /dev/sda1",  # Użycie dysku
                "free -m | grep Mem",      # Użycie pamięci
                "uptime",                  # Obciążenie systemu
                "ps aux | sort -nrk 3,3 | head -5"  # Top 5 procesów
            ]
            
            results = {}
            for cmd in commands:
                exit_code, stdout, stderr = ssh_client.execute_command(cmd)
                results[cmd] = stdout.strip()
            
            # Przetwórz wyniki przez LLM
            system_prompt = """
            Jesteś systemem monitorowania. Przeanalizuj dane o użyciu zasobów serwera i określ:
            1. Czy występują jakieś problemy (np. mało miejsca na dysku, wysokie obciążenie)
            2. Jakie są rekomendacje
            3. Czy należy wysłać alert (CRITICAL, WARNING, INFO, OK)
            
            Odpowiedź sformatuj jako JSON z polami: status, message, recommendations.
            """
            
            result = process.process_text(
                json.dumps(results, indent=2),
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            try:
                # Parsuj odpowiedź LLM jako JSON
                analysis = json.loads(result.data)
                
                # Wyślij alert przez MQTT
                mqtt_client.process_text(
                    json.dumps({
                        "type": "alert",
                        "status": analysis.get("status", "UNKNOWN"),
                        "message": analysis.get("message", ""),
                        "recommendations": analysis.get("recommendations", []),
                        "timestamp": time.time()
                    }),
                    topic="monitoring/alerts"
                )
                
                print(f"Wysłano alert: {analysis.get('status', 'UNKNOWN')} - {analysis.get('message', '')}")
            
            except json.JSONDecodeError:
                print(f"Błąd parsowania odpowiedzi LLM: {result.data}")
            
            # Czekaj przed kolejnym sprawdzeniem
            time.sleep(300)  # 5 minut
    
    except KeyboardInterrupt:
        print("Zakończono działanie systemu monitorowania.")

if __name__ == "__main__":
    run_monitoring_system()
```

### Automatyczny deployment z FTP i SSH

```python
# examples/auto_deployment.py
from ftp.client import FTPClient
from ssh.client import SSHClient
from process.process import Process
import os
import time
import json
import argparse

def deploy_application(app_path, remote_dir, config_file=None):
    # Inicjalizacja klientów
    ftp_client = FTPClient(
        host=os.environ.get("FTP_HOST", "localhost"),
        port=int(os.environ.get("FTP_PORT", "21")),
        username=os.environ.get("FTP_USERNAME", "user"),
        password=os.environ.get("FTP_PASSWORD", "password")
    )
    
    ssh_client = SSHClient(
        host=os.environ.get("SSH_HOST", "localhost"),
        port=int(os.environ.get("SSH_PORT", "22")),
        username=os.environ.get("SSH_USERNAME", "user"),
        password=os.environ.get("SSH_PASSWORD", "password")
    )
    
    # Inicjalizacja procesu LLM
    process = Process(plugin="llm")
    
    print(f"Rozpoczęto deployment aplikacji z {app_path} do {remote_dir}")
    
    # 1. Przygotuj listę plików do przesłania
    local_files = []
    for root, dirs, files in os.walk(app_path):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, app_path)
            remote_path = os.path.join(remote_dir, rel_path)
            local_files.append((local_path, remote_path))
    
    # 2. Prześlij pliki przez FTP
    for local_path, remote_path in local_files:
        print(f"Przesyłanie: {local_path} -> {remote_path}")
        ftp_client.upload_file(local_path, remote_path)
    
    # 3. Wykonaj polecenia instalacyjne przez SSH
    commands = [
        f"cd {remote_dir} && pip install -r requirements.txt",
        f"cd {remote_dir} && python setup.py develop",
        f"systemctl restart myapp.service"
    ]
    
    for cmd in commands:
        print(f"Wykonywanie: {cmd}")
        exit_code, stdout, stderr = ssh_client.execute_command(cmd)
        if exit_code != 0:
            print(f"Błąd: {stderr}")
            return False
    
    # 4. Sprawdź status aplikacji
    exit_code, stdout, stderr = ssh_client.execute_command("systemctl status myapp.service")
    
    # 5. Użyj LLM do analizy logu deploymentu
    if config_file:
        with open(config_file, "r") as f:
            config = f.read()
        
        system_prompt = """
        Jesteś asystentem DevOps. Przeanalizuj logi z deploymentu aplikacji i określ:
        1. Czy deployment zakończył się sukcesem
        2. Czy występują jakieś problemy lub ostrzeżenia
        3. Jakie są rekomendacje
        
        Weź pod uwagę konfigurację aplikacji.
        """
        
        result = process.process_text(
            f"Logi deploymentu:\n{stdout}\n\nKonfiguracja:\n{config}",
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        print("\nAnaliza deploymentu:")
        print(result.data)
    
    print("\nDeployment zakończony.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Narzędzie do automatycznego deploymentu aplikacji")
    parser.add_argument("app_path", help="Ścieżka do katalogu aplikacji")
    parser.add_argument("remote_dir", help="Ścieżka zdalna na serwerze")
    parser.add_argument("--config", help="Plik konfiguracyjny aplikacji")
    
    args = parser.parse_args()
    deploy_application(args.app_path, args.remote_dir, args.config)
```

Powyższe przykłady pokazują, jak można wykorzystać multiprotokołowe wsparcie w szablonie cookiecutter do tworzenia zaawansowanych rozwiązań z wykorzystaniem LLM jako procesu przetwarzającego dane z różnych źródeł.
