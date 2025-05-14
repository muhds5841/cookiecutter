# Integracja z LLM (Large Language Models)

Ten dokument opisuje, jak zintegrować system Process z dużymi modelami językowymi (LLM) za pomocą Model Context Protocol (MCP) oraz różnych protokołów komunikacyjnych.

## Spis treści

- [Wprowadzenie](#wprowadzenie)
- [Integracja przez MCP](#integracja-przez-mcp)
- [Protokoły komunikacyjne](#protokoły-komunikacyjne)
  - [MQTT](#mqtt)
  - [WebSocket](#websocket)
  - [EMAIL](#email)
  - [SSH](#ssh)
  - [FTP](#ftp)
- [Łączenie protokołów](#łączenie-protokołów)
- [Przykłady użycia](#przykłady-użycia)

## Wprowadzenie

System Process umożliwia integrację z dużymi modelami językowymi (LLM) poprzez różne protokoły komunikacyjne. Głównym mechanizmem integracji jest Model Context Protocol (MCP), który standaryzuje sposób komunikacji między LLM a systemem Process.

## Integracja przez MCP

Model Context Protocol (MCP) to protokół zaprojektowany do integracji z LLM jako narzędzie. MCP umożliwia modelom językowym korzystanie z funkcji systemu Process poprzez standardowy interfejs.

### Konfiguracja MCP dla LLM

1. **Uruchom serwer MCP**:

```bash
# Uruchom serwer MCP
cd mcp
python mcp_server.py
```

2. **Skonfiguruj LLM do korzystania z MCP**:

Poniżej znajduje się przykład konfiguracji dla OpenAI API:

```python
import openai
from mcp.client import MCPClient

# Inicjalizacja klienta MCP
mcp_client = MCPClient(host="localhost", port=4000)

# Pobierz definicje narzędzi MCP
tools = mcp_client.get_tools_definition()

# Konfiguracja OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Jesteś asystentem AI z dostępem do narzędzi."},
        {"role": "user", "content": "Przetwórz tekst 'Przykładowy tekst do przetworzenia'"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Obsługa odpowiedzi z wywołaniem narzędzia
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # Wywołanie narzędzia przez MCP
        tool_response = mcp_client.call_tool(tool_name, tool_args)
        
        # Przekazanie odpowiedzi z narzędzia z powrotem do LLM
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Jesteś asystentem AI z dostępem do narzędzi."},
                {"role": "user", "content": "Przetwórz tekst 'Przykładowy tekst do przetworzenia'"},
                response.choices[0].message,
                {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tool_response)}
            ],
            tools=tools,
            tool_choice="auto"
        )
```

3. **Dostępne narzędzia MCP**:

- `process_text`: Przetwarzanie tekstu przez silnik Process
- `get_resources`: Pobieranie dostępnych zasobów
- `get_status`: Sprawdzanie statusu przetwarzania
- `cancel_process`: Anulowanie przetwarzania

## Protokoły komunikacyjne

System Process obsługuje różne protokoły komunikacyjne, które można wykorzystać do integracji z LLM.

### MQTT

MQTT to lekki protokół komunikacyjny typu publish-subscribe, idealny do komunikacji IoT i systemów rozproszonych.

#### Konfiguracja MQTT dla LLM

1. **Uruchom serwer MQTT**:

```bash
cd mqtt
python server.py
```

2. **Przykład integracji z LLM**:

```python
from mqtt.client import ProcessClient

# Inicjalizacja klienta MQTT
client = ProcessClient(broker_host="localhost", broker_port=1883)

# Przetwarzanie tekstu
result = client.process_text("Przykładowy tekst do przetworzenia", language="pl-PL")
print(result)

# Pobieranie zasobów
resources = client.get_resources()
print(resources)
```

### WebSocket

WebSocket umożliwia dwukierunkową komunikację w czasie rzeczywistym między klientem a serwerem.

#### Konfiguracja WebSocket dla LLM

1. **Uruchom serwer WebSocket**:

```bash
cd websocket
python server.py
```

2. **Przykład integracji z LLM**:

```python
import asyncio
import websockets
import json

async def process_text():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        # Przygotuj żądanie
        request = {
            "type": "process",
            "request_id": "12345",
            "text": "Przykładowy tekst do przetworzenia",
            "options": {"language": "pl-PL"}
        }
        
        # Wyślij żądanie
        await websocket.send(json.dumps(request))
        
        # Odbierz odpowiedź
        response = await websocket.recv()
        return json.loads(response)

# Uruchom funkcję asynchroniczną
result = asyncio.run(process_text())
print(result)
```

### EMAIL

System Process może integrować się z protokołami pocztowymi (IMAP, SMTP, POP3) w celu przetwarzania wiadomości e-mail.

#### Struktura katalogów dla protokołów EMAIL

Każdy protokół pocztowy jest zaimplementowany jako oddzielny moduł:

```
email/
├── imap/
│   ├── server.py
│   └── client.py
├── smtp/
│   ├── server.py
│   └── client.py
├── pop3/
│   ├── server.py
│   └── client.py
└── .env.example
```

#### Konfiguracja EMAIL dla LLM

1. **Uruchom serwery EMAIL**:

```bash
cd email/imap
python server.py

cd email/smtp
python server.py
```

2. **Przykład integracji z LLM**:

```python
from email.imap.client import IMAPClient
from email.smtp.client import SMTPClient

# Inicjalizacja klienta IMAP
imap_client = IMAPClient(
    host="localhost",
    port=143,
    username="user",
    password="password"
)

# Pobierz wiadomości
messages = imap_client.get_messages(folder="INBOX", limit=10)

# Przetwórz wiadomości przez LLM
for message in messages:
    # Przetwarzanie przez LLM
    processed_content = llm.process(message.content)
    
    # Wyślij odpowiedź przez SMTP
    smtp_client = SMTPClient(
        host="localhost",
        port=25,
        username="user",
        password="password"
    )
    
    smtp_client.send_message(
        to=message.sender,
        subject=f"Re: {message.subject}",
        content=processed_content
    )
```

### SSH

Protokół SSH umożliwia bezpieczne zdalne wykonywanie poleceń i transfer plików.

#### Konfiguracja SSH dla LLM

1. **Uruchom serwer SSH**:

```bash
cd ssh
python server.py
```

2. **Przykład integracji z LLM**:

```python
from ssh.client import SSHClient

# Inicjalizacja klienta SSH
ssh_client = SSHClient(
    host="localhost",
    port=22,
    username="user",
    password="password"
)

# Wykonaj polecenie
result = ssh_client.execute_command("ls -la")
print(result)

# Transfer plików
ssh_client.upload_file(local_path="local.txt", remote_path="/remote/path/remote.txt")
ssh_client.download_file(remote_path="/remote/path/data.txt", local_path="downloaded.txt")
```

### FTP

Protokół FTP służy do transferu plików między klientem a serwerem.

#### Konfiguracja FTP dla LLM

1. **Uruchom serwer FTP**:

```bash
cd ftp
python server.py
```

2. **Przykład integracji z LLM**:

```python
from ftp.client import FTPClient

# Inicjalizacja klienta FTP
ftp_client = FTPClient(
    host="localhost",
    port=21,
    username="user",
    password="password"
)

# Listowanie plików
files = ftp_client.list_files("/remote/path")
print(files)

# Transfer plików
ftp_client.upload_file(local_path="local.txt", remote_path="/remote/path/remote.txt")
ftp_client.download_file(remote_path="/remote/path/data.txt", local_path="downloaded.txt")
```

## Łączenie protokołów

MCP umożliwia łączenie różnych protokołów jako źródeł danych dla LLM. Dzięki warstwie abstrakcji w MCP, można korzystać z danych pochodzących z różnych protokołów w jednolity sposób.

### Przykład łączenia protokołów przez MCP

```python
from mcp.client import MCPClient
from mcp.tools import register_tool

# Inicjalizacja klienta MCP
mcp_client = MCPClient(host="localhost", port=4000)

# Rejestracja narzędzi dla różnych protokołów
register_tool(
    "get_email_attachments",
    lambda folder, limit: email_client.get_attachments(folder, limit),
    description="Pobiera załączniki z wiadomości e-mail"
)

register_tool(
    "upload_to_ftp",
    lambda file_path, remote_path: ftp_client.upload_file(file_path, remote_path),
    description="Przesyła plik na serwer FTP"
)

register_tool(
    "execute_ssh_command",
    lambda command: ssh_client.execute_command(command),
    description="Wykonuje polecenie przez SSH"
)

# Przykład przepływu pracy łączącego protokoły
def process_email_attachments_and_upload():
    # 1. Pobierz załączniki z e-maila przez IMAP
    attachments = mcp_client.call_tool("get_email_attachments", {"folder": "INBOX", "limit": 5})
    
    # 2. Przetwórz każdy załącznik przez Process
    for attachment in attachments:
        processed_data = mcp_client.call_tool("process_text", {"text": attachment.content})
        
        # 3. Zapisz wyniki lokalnie
        with open(f"processed_{attachment.filename}", "w") as f:
            f.write(processed_data)
        
        # 4. Prześlij przetworzone pliki na serwer FTP
        mcp_client.call_tool("upload_to_ftp", {
            "file_path": f"processed_{attachment.filename}",
            "remote_path": f"/processed/{attachment.filename}"
        })
        
        # 5. Wykonaj polecenie na serwerze przez SSH (np. zmiana uprawnień)
        mcp_client.call_tool("execute_ssh_command", {
            "command": f"chmod 644 /processed/{attachment.filename}"
        })
```

## Przykłady użycia

### Przetwarzanie dokumentów z różnych źródeł

```python
# Przykład przepływu pracy dla przetwarzania dokumentów
def process_documents_from_multiple_sources():
    # 1. Pobierz dokumenty z e-maila
    email_docs = mcp_client.call_tool("get_email_attachments", {"folder": "INBOX", "limit": 10})
    
    # 2. Pobierz dokumenty z FTP
    ftp_docs = mcp_client.call_tool("list_files", {"path": "/documents"})
    ftp_doc_contents = []
    for doc in ftp_docs:
        content = mcp_client.call_tool("download_from_ftp", {"remote_path": doc.path})
        ftp_doc_contents.append(content)
    
    # 3. Połącz dokumenty z różnych źródeł
    all_docs = email_docs + ftp_doc_contents
    
    # 4. Przetwórz wszystkie dokumenty przez Process
    results = []
    for doc in all_docs:
        processed = mcp_client.call_tool("process_text", {"text": doc.content})
        results.append(processed)
    
    # 5. Wyślij wyniki przez SMTP
    mcp_client.call_tool("send_email", {
        "to": "user@example.com",
        "subject": "Wyniki przetwarzania dokumentów",
        "content": "\n".join(results)
    })
```

### Automatyzacja deploymentu przez SSH i FTP

```python
# Przykład automatyzacji deploymentu przez SSH i FTP
def deploy_application():
    # 1. Przygotuj pliki do deploymentu
    files_to_deploy = ["/path/to/app.py", "/path/to/config.json"]
    
    # 2. Prześlij pliki na serwer przez FTP
    for file in files_to_deploy:
        mcp_client.call_tool("upload_to_ftp", {
            "file_path": file,
            "remote_path": f"/app/{os.path.basename(file)}"
        })
    
    # 3. Wykonaj polecenia na serwerze przez SSH
    mcp_client.call_tool("execute_ssh_command", {"command": "cd /app && pip install -r requirements.txt"})
    mcp_client.call_tool("execute_ssh_command", {"command": "systemctl restart myapp.service"})
    
    # 4. Sprawdź status aplikacji
    status = mcp_client.call_tool("execute_ssh_command", {"command": "systemctl status myapp.service"})
    
    # 5. Wyślij powiadomienie o statusie deploymentu
    mcp_client.call_tool("send_email", {
        "to": "admin@example.com",
        "subject": "Status deploymentu aplikacji",
        "content": status
    })
```

Powyższe przykłady pokazują, jak można łączyć różne protokoły komunikacyjne za pomocą MCP, aby tworzyć złożone przepływy pracy dla LLM.