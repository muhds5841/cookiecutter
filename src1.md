project/
├── core/                  # Wspólne elementy infrastruktury
│   ├── config_manager.py  # Już masz
│   ├── error_handling.py  # Już masz
│   ├── logging.py         # Już masz
│   └── utils.py           # Już masz
│
├── audio_input/           # Moduł wejścia audio
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── adapter_base.py        # Klasa bazowa
│   │   ├── pulseaudio_adapter.py  # PulseAudio
│   │   ├── alsa_adapter.py        # ALSA
│   │   └── pyaudio_adapter.py     # PyAudio
│   ├── device_manager.py          # Zarządzanie urządzeniami wejściowymi
│   ├── audio_service.py           # Główny serwis audio
│   ├── Dockerfile                 # Specyficzny Dockerfile
│   └── requirements.txt           # Specyficzne zależności
│
├── audio_output/          # Moduł wyjścia audio
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── adapter_base.py        # Klasa bazowa
│   │   ├── pulseaudio_adapter.py  # PulseAudio
│   │   ├── alsa_adapter.py        # ALSA
│   │   └── pyaudio_adapter.py     # PyAudio
│   ├── device_manager.py          # Zarządzanie urządzeniami wyjściowymi
│   ├── audio_service.py           # Główny serwis odtwarzania audio
│   ├── Dockerfile                 # Specyficzny Dockerfile
│   └── requirements.txt           # Specyficzne zależności
│
├── audio_streaming/       # Moduł strumieniowania audio
│   ├── streaming_manager.py      # Zarządzanie strumieniami audio
│   ├── stream_processor.py       # Przetwarzanie strumieni
│   ├── Dockerfile                # Specyficzny Dockerfile
│   └── requirements.txt          # Specyficzne zależności
│
├── tts/                   # Moduł TTS (osobny, niezależny)
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── tts_adapter_base.py     # Klasa bazowa
│   │   ├── espeak_adapter.py       # eSpeak
│   │   ├── festival_adapter.py     # Festival
│   │   └── pyttsx3_adapter.py      # pyttsx3
│   ├── service.py                  # Główny serwis TTS
│   ├── Dockerfile                  # Specyficzny Dockerfile
│   └── requirements.txt            # Specyficzne zależności
│
├── stt/                   # Moduł STT (osobny, niezależny)
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── stt_adapter_base.py     # Klasa bazowa
│   │   ├── sphinx_adapter.py       # PocketSphinx
│   │   ├── vosk_adapter.py         # Vosk
│   │   └── sr_adapter.py           # SpeechRecognition
│   ├── service.py                  # Główny serwis STT
│   ├── Dockerfile                  # Specyficzny Dockerfile
│   └── requirements.txt            # Specyficzne zależności
│
├── grpc/                 # Serwer i klient gRPC
│   ├── proto/
│   │   ├── audio_input.proto    # Definicje dla audio_input
│   │   ├── audio_output.proto   # Definicje dla audio_output
│   │   ├── audio_stream.proto   # Definicje dla strumieniowania
│   │   ├── tts.proto            # Definicje dla TTS
│   │   └── stt.proto            # Definicje dla STT
│   ├── server.py          # Główny serwer gRPC
│   ├── client.py          # Główny klient gRPC
│   ├── services/          # Implementacje serwisów
│   │   ├── audio_input_service.py
│   │   ├── audio_output_service.py
│   │   ├── audio_stream_service.py
│   │   ├── tts_service.py
│   │   └── stt_service.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── rest/                 # Serwer i klient REST API
│   ├── controllers/
│   │   ├── audio_input_controller.py
│   │   ├── audio_output_controller.py
│   │   ├── audio_stream_controller.py
│   │   ├── tts_controller.py
│   │   └── stt_controller.py
│   ├── server.py
│   ├── client.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── webrtc/               # Obsługa WebRTC
│   ├── signaling.py       # Sygnalizacja WebRTC
│   ├── stream_handler.py  # Obsługa strumieni WebRTC
│   ├── server.py          # Serwer WebRTC
│   ├── client.py          # Klient WebRTC
│   ├── Dockerfile
│   └── requirements.txt
│
└── docker-compose.yml    # Orkiestracja wszystkich kontenerów