cookiecutter-tts-project/
├── cookiecutter.json                  # Konfiguracja szablonu
├── README.md                          # Dokumentacja szablonu
├── hooks/                             # Skrypty hook
│   ├── pre_gen_project.py             # Uruchamiany przed generowaniem
│   └── post_gen_project.py            # Uruchamiany po wygenerowaniu projektu
└── {{cookiecutter.project_slug}}/     # Katalog szablonu projektu
    ├── docker-compose.yml
    ├── Makefile                       # Główny Makefile
    ├── pyproject.toml                 # Konfiguracja Poetry
    ├── README.md                      # Dokumentacja projektu
    ├── .gitignore                     # Pliki ignorowane przez Git
    ├── lib/                           # Wspólne biblioteki
    │   ├── __init__.py
    │   ├── config.py
    │   ├── logging.py
    │   ├── utils.py
    │   └── quality/                   # Narzędzia jakości kodu
    ├── tts_engine/                    # Silnik 
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── __init__.py
    │   ├── tts_engine.py
    │   └── adapters/                  # Adaptery dla różnych silników 
    ├── mcp/                           # Komponent MCP (nowy/rozszerzony)
    │   ├── Dockerfile
    │   ├── pyproject.toml
    │   ├── mcp_server.py              # Serwer MCP
    │   ├── transports/                # Implementacje transportu
    │   │   ├── __init__.py
    │   │   ├── sse.py                 # Server-Sent Events
    │   │   ├── stdio.py               # Komunikacja przez stdout/stdin
    │   │   └── hybrid.py              # Wieloprotokołowy serwer
    │   ├── protocol/                  # Obsługa protokołu MCP
    │   │   ├── __init__.py
    │   │   ├── negotiation.py         # Negocjacja wersji
    │   │   └── discovery.py           # Wykrywanie narzędzi
    │   ├── tools/                     # Narzędzia MCP
    │   │   ├── __init__.py
    │   │   └── tts_tool.py            # Narzędzie 
    │   ├── resources/                 # Zasoby MCP
    │   │   ├── __init__.py
    │   │   └── uri_templates.py       # Definicje URI templates
    │   └── sampling/                  # Strategie próbkowania dla LLM
    │       ├── __init__.py
    │       └── adaptive.py            # Adaptacyjne próbkowanie
    ├── grpc/                          # Serwis gRPC
    ├── rest/                          # Serwis REST
    ├── webrtc/                        # Serwis WebRTC
    ├── shell/                         # CLI
    └── tests/                         # Testy
        ├── __init__.py
        ├── conftest.py
        └── mcp_tests/                 # Testy komponentów MCP
            ├── __init__.py
            ├── test_transports.py
            ├── test_protocol.py
            └── test_tools.py