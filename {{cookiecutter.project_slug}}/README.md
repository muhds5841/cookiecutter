# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Struktura projektu

{% if cookiecutter.components.tts_engine %}
- tts_engine/                # Silnik TTS
  ├── Dockerfile
  ├── pyproject.toml
  ├── __init__.py
  ├── tts_engine.py
  └── adapters/             # Adaptery dla różnych silników TTS
{% endif %}
{% if cookiecutter.components.mcp %}
- mcp/                       # Komponent MCP
  ├── Dockerfile
  ├── pyproject.toml
  ├── mcp_server.py          # Serwer MCP
  ├── transports/            # Implementacje transportu (SSE, stdio, hybrid)
  ├── protocol/              # Obsługa protokołu MCP
  ├── tools/                 # Narzędzia MCP
  ├── resources/             # Zasoby MCP z URI templates
  └── sampling/              # Strategie próbkowania dla LLM
{% endif %}
{% if cookiecutter.components.grpc %}
- grpc/                      # Serwis gRPC
{% endif %}
{% if cookiecutter.components.rest %}
- rest/                      # Serwis REST API
{% endif %}
{% if cookiecutter.components.webrtc %}
- webrtc/                    # Serwis WebRTC
{% endif %}
{% if cookiecutter.components.shell %}
- shell/                     # Interfejs CLI
{% endif %}
- lib/                       # Wspólne biblioteki
- quality/                   # Konfiguracje QA
- tests/                     # Testy

## Funkcjonalności

{% if cookiecutter.components.tts_engine %}
- Silnik syntezy mowy z obsługą wielu silników (coqui, google, aws)
{% endif %}
{% if cookiecutter.components.mcp %}
- Integracja z Model Context Protocol (MCP) umożliwiająca łatwą integrację z LLM
- Wsparcie dla transportów MCP: {% if cookiecutter.mcp_configuration.transports.sse %}SSE{% endif %}{% if cookiecutter.mcp_configuration.transports.stdio %}, stdio{% endif %}{% if cookiecutter.mcp_configuration.transports.grpc %}, gRPC{% endif %}
{% if cookiecutter.mcp_configuration.include_discovery %}
- Automatyczne wykrywanie narzędzi
{% endif %}
{% if cookiecutter.mcp_configuration.include_tool_registry %}
- Rejestr narzędzi i URI templates
{% endif %}
{% if cookiecutter.mcp_configuration.include_adaptive_sampling %}
- Adaptacyjne próbkowanie dla LLM
{% endif %}
{% endif %}
{% if cookiecutter.components.grpc %}
- Interfejs gRPC
{% endif %}
{% if cookiecutter.components.rest %}
- Interfejs REST API
{% endif %}
{% if cookiecutter.components.webrtc %}
- Wsparcie dla WebRTC
{% endif %}
{% if cookiecutter.components.shell %}
- Interfejs wiersza poleceń
{% endif %}

## Instalacja

```bash
# Instalacja zależności
poetry install

# Konfiguracja narzędzi jakości kodu
pre-commit install