# Cookiecutter Modular Project Template

> **Quickstart:**
> 1. Install Cookiecutter:
>    ```bash
>    pip install cookiecutter
>    ```
> 2. Generate your project:
>    ```bash
>    cookiecutter gh:pyfunc/cookiecutter
>    ```
> 3. Answer prompts to select name, protocols, services, etc.
> 4. Enter the generated directory and follow the instructions below.
>
> **Navigation:** Use the menu for quick access to any section.

---

## Menu
- [Solution Overview](#solution-overview)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [How to Use the Modules](#how-to-use-the-modules)
- [Tool Installation](#tool-installation)
- [Project Installation](#project-installation)
- [Running the Project](#running-the-project)
- [Plugin Development](#plugin-development)
- [Environment Configuration](#environment-configuration)
- [Testing](#testing)
- [Additional Resources](#additional-resources)
- [About Tom Sapletta](#about-tom-sapletta)

---

> **Coming Soon:**
> The next release will introduce standardized modules, letting you add new services and protocols (e.g., GraphQL, AMQP) to your Cookiecutter project with just a few steps—either at generation time or later as plug-and-play modules.

---

## Solution Overview

This template enables you to build modular, multi-protocol, production-ready backend systems. Each service or protocol lives in its own directory, with independent configuration, dependencies, and Dockerfile. You can rapidly prototype, scale, and extend your system for edge, cloud, IoT, and AI/LLM-powered applications.

---

## Requirements
- Python 3.8+
- pipx (recommended)
- Poetry (recommended)

---

## Project Structure

```
.
├── core
│   ├── config_manager.py
│   ├── ...
├── grpc
│   ├── server.py
│   ├── client.py
│   ├── Dockerfile
│   └── ...
├── rest
│   ├── server.py
│   ├── client.py
│   ├── Dockerfile
│   └── ...
├── mqtt
│   ├── server.py
│   ├── client.py
│   ├── Dockerfile
│   └── ...
├── process
│   ├── plugin_system.py
│   └── plugins
│       └── my_plugin.py
└── ...
```

---

## How to Use the Modules

---

## Tool Installation

### pipx

**Linux/macOS:**
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```
**Ubuntu:**
```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```
**macOS:**
```bash
brew install pipx
pipx ensurepath
```
**Windows:**
```powershell
py -m pip install --user pipx
.\pipx.exe ensurepath
```

### Poetry

**Linux/macOS:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
**Windows:**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```
Check installation:
```bash
poetry --version
```

---

### Project Installation

1. Clone the repository or generate a project with cookiecutter:
    ```bash
    pip install cookiecutter
    cookiecutter gh:pyfunc/cookiecutter
    ```
2. Enter the project directory.
3. Install dependencies:
    ```bash
    poetry install
    ```

---

### Generate Your Project

```bash
cookiecutter gh:pyfunc/cookiecutter
```
You will be prompted to select project name, description, author, protocols (gRPC, REST, MQTT, etc.), and other options. Example prompt:

```
[1/25] project_name ( Project): tts
[2/25] project_slug (tts):
[3/25] project_description (A modular text-to-speech system with MCP integration):
...
[6/25] Select license
  1 - MIT
  2 - Apache-2.0
  3 - GPL-3.0
  4 - BSD-3-Clause
  Choose from [1/2/3/4] (1):
...
```

### Install Poetry (Dependency Manager)

#### Linux/macOS
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
#### Windows (PowerShell)
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```
Check installation:
```bash
poetry --version
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Activate the Environment

```bash
poetry shell
```

### 5. Run Services

Each protocol/service (gRPC, REST, MQTT, etc.) can be run independently. For example:

```bash
poetry run python grpc/server.py
poetry run python rest/server.py
```
Or use Makefile/Docker Compose if available:
```bash
make up
```

### 6. Add or Extend Modules

- To add a new protocol/service, create a new directory (e.g., `graphql/`), add your `server.py`, `client.py`, and `Dockerfile`.
- Register new plugins in `process/plugins/`.
- Use environment variables for configuration.

#### Example: Adding a Custom Plugin

```python
# process/plugins/my_text_plugin.py
from process.process_base import ProcessBase
from process.plugin_system import register_plugin

class MyTextPlugin(ProcessBase):
    def process_text(self, text, **kwargs):
        return self.create_result(
            data=text[::-1],
            format='text',
            metadata={'plugin': 'my_text_plugin'}
        )

register_plugin('my_text_plugin', MyTextPlugin)
```

---

## Tool Installation

See above for Poetry. For pipx:
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

---

## Project Installation

See steps above (Poetry, dependencies, environment activation).

---

## Running the Project

See "How to Use the Modules" above for running individual services or all at once.

---

## Plugin Development

See example above. Place your plugin in `process/plugins/`, inherit from `ProcessBase`, and register it.

---

## Environment Configuration

Copy `.env.example` to `.env` in the main directory or for each module as needed. Use environment variable prefixes for each component: `CORE_*`, `PROCESS_*`, `GRPC_*`, etc.

---

## Testing

Run tests for all modules:
```bash
make test
```
Or for a specific module:
```bash
cd process
poetry run pytest
```



## Solution Overview

This project provides a highly modular, extensible, and production-ready template for building multi-service, multi-protocol applications. Its architecture is designed to support rapid development, easy integration, and scalable deployment of various backend services—each encapsulated in its own module and container.

### What is this solution for?

- **Rapid Prototyping:** Quickly scaffold new projects with best practices for code quality, testing, and deployment.
- **Multi-Protocol Support:** Out-of-the-box support for gRPC, REST, MQTT, WebRTC, WebSocket, IMAP, FTP, and more.
- **Separation of Concerns:** Each service (e.g., API, messaging, processing) lives in its own directory, with its own dependencies, configuration, and Dockerfile.
- **Edge, Cloud, and IoT:** Suitable for distributed, cloud-native, and edge computing scenarios.
- **AI/LLM Integration:** Ready for Model Context Protocol (MCP), LangChain, and other AI/LLM integrations.

### Future Possibilities & Extensibility

The architecture is designed to grow with your needs:

- **Add New Protocols Easily:** Create new directories (e.g., `graphql`, `coap`, `amqp`), add a Dockerfile and service code, and integrate with the rest of the stack.
- **Polyglot Services:** Implement services in different languages (Python, Go, Node.js, etc.)—each can have its own tech stack and dependencies.
- **Plug-and-Play Modules:** Swap, upgrade, or remove services without affecting the rest of the system.
- **Custom Plugins:** Extend the core processing engine with your own plugins, registered dynamically.
- **AI/LLM Expansion:** Integrate new AI models, NLP pipelines, or ML inference endpoints as independent modules.
- **Scalable Deployment:** Each service can be scaled independently using Docker Compose, Kubernetes, or serverless platforms.


init your repository and run:

```bash
cookiecutter gh:pyfunc/cookiecutter
```
result
```bash
You've downloaded /home/tom/.cookiecutters/cookiecutter before. Is it okay to delete and re-download it? [y/n] (y): y
  [1/25] project_name ( Project): tts
  [2/25] project_slug (tts): 
  [3/25] project_description (A modular text-to-speech system with MCP integration): 
  [4/25] author_name (Tom Sapletta): 
  [5/25] author_email (info@softreck.dev): 
  [6/25] Select license
    1 - MIT
    2 - Apache-2.0
    3 - GPL-3.0
    4 - BSD-3-Clause
    Choose from [1/2/3/4] (1): 
  [7/25] Select python_version
```


### Example: Adding a New Service

Suppose you want to add a GraphQL API:

1. **Create a new directory:**
    ```bash
    mkdir graphql
    cd graphql
    poetry init
    ```
2. **Add dependencies:**
    ```bash
    poetry add strawberry-graphql fastapi uvicorn
    ```
3. **Create service files:**
    - `server.py` (GraphQL server)
    - `client.py` (optional client)
    - `Dockerfile` (containerization)
4. **Integrate with other modules:**
    - Use shared environment variables, connect to the process engine, or expose new endpoints.

### Example: Integrating a New Protocol

To add support for AMQP (RabbitMQ):

- Create an `amqp/` directory with `server.py`, `client.py`, and a `Dockerfile`.
- Add AMQP client/server logic using `pika` (Python) or `amqplib` (Node.js).
- Register the AMQP service in your orchestration (Docker Compose, Kubernetes).

### Example: Custom Plugin for Text Processing

```python
# process/plugins/my_text_plugin.py
from process.process_base import ProcessBase
from process.plugin_system import register_plugin

class MyTextPlugin(ProcessBase):
    def process_text(self, text, **kwargs):
        # Custom text transformation
        return self.create_result(
            data=text[::-1],  # Example: reverse text
            format='text',
            metadata={'plugin': 'my_text_plugin'}
        )

register_plugin('my_text_plugin', MyTextPlugin)
```

### Modular Architecture Benefits

- **Independent Components:** Each service (gRPC, REST, MCP, MQTT, WebSocket, etc.) can run as a standalone repository or within the same monorepo.
- **Language Independence:** Services can be implemented in Python, Go, Node.js, or any language.
- **Minimal Coupling:** Each module only depends on what it needs.
- **Standardized Interfaces:** Clear API contracts and communication protocols.
- **Shared Tools:** Common utilities are available but not required.

### AI/LLM Integration

- **MCP (Model Context Protocol):** Standard protocol for integrating with LLMs and AI tools.
- **LangChain:** Easily add LLM-powered chains and agents.
- **MQTT/WebSocket:** Connect to real-time systems, IoT devices, or chatbots.

### Why This Structure?

- **Separate Dockerfiles:** Tailor environments for each service.
- **Modular:** Develop, test, and deploy services independently.
- **Clear Boundaries:** Each service has its own directory, configuration, and lifecycle.
- **Easy Code Generation:** Consistent structure enables automated code generation and scaffolding.

For more details, see the [Modular Architecture](docs/modular_architecture.md) and [Developer Guide](docs/developer_guide.md).


## Full Project Structure

```
.  
├── core
│   ├── config_manager.py
│   ├── config.py
│   ├── error_handling.py
│   ├── __init__.py
│   ├── logging.py
│   ├── monitoring.py
│   ├── README.md
│   ├── scaffold.py
│   ├── test_config.py
│   └── utils.py
├── deploy
│   ├── ansible
│   ├── fabfile.py
│   ├── kubernetes
│   └── scripts
├── dev_setup.py
├── docker-compose.prod.yml
├── docker-compose.yml
├── ftp
│   ├── client.py
│   ├── __init__.py
│   ├── server.py
│   ├── test_ftp_client.py
│   └── test_ftp_server.py
├── grpc
│   ├── client.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── Makefile
│   ├── proto
│   ├── pyproject.toml
│   ├── server.py
│   └── test_grpc.py
├── hooks
│   ├── post_gen_project.py
│   └── pre_gen_project.py
├── imap
│   ├── client.py
│   ├── server.py
│   └── test_imap_client.py
├── langchain
├── Makefile
├── mcp
│   ├── Dockerfile
│   ├── __init__.py
│   ├── Makefile
│   ├── mcp_server.py
│   ├── process
│   ├── protocol
│   ├── pyproject.toml
│   ├── README.md
│   ├── resources
│   ├── sampling
│   ├── tests
│   ├── tools
│   └── transports
├── mqtt
│   ├── client.py
│   ├── __init__.py
│   ├── server.py
│   ├── test_mqtt_client.py
│   └── test_mqtt_server.py
├── process
│   ├── adapters
│   ├── Dockerfile
│   ├── __init__.py
│   ├── languages.py
│   ├── Makefile
│   ├── plugin_system.py
│   ├── process_base.py
│   ├── process_config.py
│   ├── process.py
│   ├── process.py.bak
│   ├── pyproject.toml
│   ├── README.md
│   └── test_process.py
├── pyproject.toml
├── quality
│   ├── bandit.yaml
│   ├── conftest.py
│   ├── doc_checker.py
│   ├── formatters.py
│   ├── hooks.py
│   ├── __init__.py
│   ├── linters.py
│   ├── Makefile
│   ├── pyproject.toml
│   ├── reporters.py
│   ├── security.py
│   ├── testers.py
│   └── tox.ini
├── README.md
├── rest
│   ├── client.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── Makefile
│   ├── models
│   ├── pyproject.toml
│   ├── server.py
│   └── test_rest.py
├── scripts
│   └── quality.sh
├── shell
│   ├── client.py
│   ├── __init__.py
│   ├── interactive.py
│   ├── main.py
│   ├── Makefile
│   └── pyproject.toml
├── tests
│   ├── conftest.py
│   ├── e2e_tests
│   ├── __init__.py
│   └── __pycache__
├── webrtc
│   ├── client.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── Makefile
│   ├── pyproject.toml
│   ├── session.py
│   ├── signaling.py
│   ├── static
│   ├── test_webrtc.py
│   └── test_websocket_client.py
└── websocket
    ├── client.py
    └── server.py
```



## Additional Resources
- [pipx Documentation](https://pipx.pypa.io/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Developer Guide](docs/developer_guide.md)
- [Modular Architecture](docs/modular_architecture.md)

---

## About Tom Sapletta

### Professional Overview
With over 12 years of experience as a DevOps Engineer, Software Developer, and Systems Architect, I specialize in creating human-technology connections through innovative solutions. My expertise spans edge computing, hypermodularization, and automated software development lifecycles, focusing on building bridges between complex technical requirements and human needs.

Currently, as the founder and CEO of Telemonit, I'm developing Portigen—an innovative power supply system with integrated edge computing functionality that enables natural human-machine interactions even in environments with limited connectivity.

### Areas of Expertise
- **DevOps & Cloud Engineering:** Docker, Kubernetes, CI/CD pipelines, infrastructure automation
- **Software Development:** Java, Python, PHP, NodeJS, microservices architecture
- **Edge Computing & IoT:** Distributed systems, sensor networks, real-time processing
- **Hardware-Software Integration:** Embedded systems, power management solutions
- **Research:** TextToSoftware, Hypermodularization, Model-Based Systems Engineering

### Notable Projects
- **Portigen:** Innovative power supply with edge computing, 500Wh capacity, ultra-low latency, modular design for IoT/edge scenarios.
- **TextToSoftware Ecosystem:** Systems converting natural language into functional applications, bridging human communication and code generation.
- **Python Packages:** Creator of pifunc, mdirtree, markdown2code, dynapsys, and more—focusing on automation, modularity, and DSLs.

### Publications & Creative Works
- "System sterowania dla osób niepełnosprawnych" (Control System for People with Disabilities) – Elektronika dla Wszystkich, 1999
- "Hexagonal Sandbox with Smartphones" – Illustrated book explaining hypermodularization for children
- Hyper Modularity – Software modularization insights

### Last Professional Experience
- **Telemonit, Frankfurt Oder**
  - Founder & CEO, Hardware and Software Developer (06.2024 – Present)
  - Leading development and production of Portigen energy supply stations with edge computing
- **Link11 GmbH, Frankfurt**
  - DevOps Engineer CDN/DNS (07.2023 – 01.2024)
  - Optimized CDN/DNS services for improved security and performance
- **IT-NRW (SEVEN PRINCIPLES AG), Düsseldorf**
  - Java Developer and DevOps (09.2020 - 04.2023)
  - Developed integration platforms for public service applications

### Research Interests
- TextToSoftware: Automated Code Generation from Natural Language
- Hypermodularization in Software Architecture
- Edge Computing and Distributed Systems
- Model-Based Systems Engineering (MBSE)
- Component-Based Software Development
- Digital Twin Technology

### Collaboration Opportunities
I welcome collaboration in edge computing, hypermodularization, text-to-software technologies, and open-source hardware/software development. Especially interested in projects bridging academic research with practical industry applications and technology education initiatives.

### Contact Information
- **ORCID:** 0009-0000-6327-2810
- **GitHub:** [tom-sapletta-com](https://github.com/tom-sapletta-com)
- **PyPI:** [Python Packages](https://pypi.org/user/tom-sapletta-com/)
- **LinkedIn:** [Tom Sapletta](https://www.linkedin.com/in/tom-sapletta/)
- **English Blog:** [tom.sapletta.com](https://tom.sapletta.com)
- **Deutsch:** [tom.sapletta.de](https://tom.sapletta.de)
- **Polski:** [tom.sapletta.pl](https://tom.sapletta.pl)
- [Softreck, Software Development](https://softreck.com)
- [Telemonit, Hardware Development](https://telemonit.com)

#### Areas of Expertise
Hypermodularity, ModDevOps, Edge Computing, MBSE, Text to Software, Python, DSL, Automation, DevOps, Digital Twin

#### Research Areas
- TextToSoftware: Automated Code Generation from Natural Language
- Hypermodularization in Software Architecture and Development
- Edge Computing and Distributed Systems
- Model-Based Systems and Software Engineering (MBSE and ModDevOps)
- Component-Based Software Development (CBSD)
- Digital Twin Technology
- Open Source Development Methodologies
- Hardware-Software Integration

#### Open Source Projects
- [Modules.webstream.dev](https://modules.webstream.dev) – WebStream modular solutions

#### Services Offered
- **Infrastructure Development:** DevOps, Cloud Engineer, Solutions Architect
- **Software Development:** Python, Java, Kotlin, Scala, JavaScript, TypeScript, Node.js, PHP
- **Hardware Development:** Network, IoT, Mobile Servers
- **SaaS Services:**
  - Automatyzer.com (Automation)
  - OneDayRun.com (One-day SaaS services)
