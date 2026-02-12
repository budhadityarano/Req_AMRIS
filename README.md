# ABS Requirements - ASPICE Compliant Automotive Requirements

This repository contains the requirements specification for the **Anti-Lock Braking System (ABS)** following the **ASPICE (Automotive SPICE)** process model. Requirements are written in RST format using [sphinx-needs](https://sphinx-needs.readthedocs.io/) objects.

## Project Structure

```
Req_AMRIS/
├── Req/                        # Sphinx source directory
│   ├── conf.py                 # Sphinx configuration
│   ├── index.rst               # Main documentation index
│   ├── SYS1/                   # SYS.1 - Stakeholder Requirements
│   ├── SYS2/                   # SYS.2 - System Requirements
│   ├── SYS3/                   # SYS.3 - System Architecture
│   ├── SWE1/                   # SWE.1 - Software Requirements
│   ├── SWE2/                   # SWE.2 - Software Architecture
│   ├── SWE3/                   # SWE.3 - Software Detailed Design
│   ├── traceability/           # Traceability matrices
│   └── future_scope/           # RAG system architecture plan
├── build/                      # Generated HTML output (gitignored)
├── Makefile                    # Build commands
└── requirements.txt            # Python dependencies
```

## ASPICE Process Coverage (Left side of V-model)

| Process Area | Description                    | Work Products                |
|:------------|:-------------------------------|:-----------------------------|
| **SYS.1**   | Stakeholder Requirements       | 10 Stakeholder Requirements  |
| **SYS.2**   | System Requirements Analysis   | 20 System Requirements       |
| **SYS.3**   | System Architectural Design    | 5 Architecture Specs + UML   |
| **SWE.1**   | Software Requirements Analysis | 50 Software Requirements     |
| **SWE.2**   | Software Architectural Design  | 5 SW Architecture Specs + UML|
| **SWE.3**   | Software Detailed Design       | 5 Detailed Design Specs      |

## Quick Start

### 1. Install Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt

# PlantUML (required for architecture diagrams)
# macOS:
brew install plantuml

# Ubuntu/Debian:
sudo apt-get install plantuml

# Windows (using Chocolatey):
choco install plantuml
```

### 2. Build HTML Documentation

```bash
make html
```

Open `build/html/index.html` in your browser.

### 3. Export needs.json (for RAG system)

```bash
make needs
```

This exports `build/needs/needs.json` — a structured JSON file containing all requirement data for use in the RAG system.

## Requirement Types

| Directive     | ASPICE Process | Example ID       |
|:-------------|:---------------|:-----------------|
| `stkh_req`   | SYS.1          | `STKH_REQ_001`   |
| `sys_req`    | SYS.2          | `SYS_REQ_001`    |
| `sys_arch`   | SYS.3          | `SYS_ARCH_001`   |
| `sw_req`     | SWE.1          | `SW_REQ_001`     |
| `sw_arch`    | SWE.2          | `SW_ARCH_001`    |
| `sw_design`  | SWE.3          | `SW_DESIGN_001`  |

## Traceability Links

```
STKH_REQ  ←[satisfies]─  SYS_REQ
SYS_REQ   ←[derives_from]─  SYS_ARCH
SYS_REQ   ←[derives_from]─  SW_REQ
SYS_ARCH  ←[traces_to]─  SW_REQ
SYS_ARCH  ←[refines]─  SW_ARCH
SW_REQ    ←[traces_to]─  SW_DESIGN
SW_ARCH   ←[refines]─  SW_DESIGN
```

## Future Scope: RAG System

See `Req/future_scope/rag_architecture.rst` for the planned RAG (Retrieval-Augmented Generation) system that will enable natural language Q&A over this requirements corpus.

**Planned stack:**
- **Vector DB:** ChromaDB / Qdrant for semantic search
- **Graph DB:** NetworkX / Neo4j for requirement relationship traversal
- **Embeddings:** sentence-transformers for text, CLIP for architecture diagrams
- **LLM:** Claude API or local Ollama for answer generation
- **Framework:** LangChain / LlamaIndex for RAG orchestration
