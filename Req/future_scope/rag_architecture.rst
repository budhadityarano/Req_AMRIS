.. _rag_architecture:

RAG System Architecture for ABS Requirements
=============================================

.. contents::
   :local:
   :depth: 2

**Document:** RAG-ARCH-PLAN-001
**Version:** 0.1 (Draft)
**Status:** Planned — Not yet implemented

This document describes the planned **Retrieval-Augmented Generation (RAG)** system
that will enable natural language querying over the ABS requirements corpus stored
in this repository.

----

Overview
---------

The RAG system will allow engineers to ask questions like:

- *"Which software requirements derive from SYS_REQ_007?"*
- *"What are all ASIL-D requirements related to wheel speed sensing?"*
- *"Show me the ABS state machine transitions."*
- *"Which requirements need test-based verification?"*

And receive accurate, traceable answers grounded in the actual documentation.

----

System Architecture
--------------------

.. uml::
   :caption: RAG System Data Pipeline

   @startuml RAG_Architecture
   skinparam packageStyle rectangle
   skinparam backgroundColor #FAFAFA
   skinparam component {
     BackgroundColor #E8EAF6
     BorderColor #3F51B5
   }

   title ABS Requirements RAG System Architecture

   package "Data Sources" as DS {
     [RST Requirements\nFiles (*.rst)] as RST
     [PlantUML Architecture\nDiagrams (*.puml)] as PUML
     [needs.json\n(Sphinx export)] as JSON
   }

   package "Ingestion Pipeline" as INGEST {
     [RST Parser\n(docutils)] as PARSER
     [PlantUML Renderer\n(PNG output)] as RENDERER
     [needs.json\nLoader] as LOADER
     [Text Chunker\n(by need item)] as CHUNKER
   }

   package "Embedding Layer" as EMBED {
     [Text Embedder\n(sentence-transformers)] as TEXT_EMB
     [Image Embedder\n(CLIP)] as IMG_EMB
   }

   package "Storage Layer" as STORE {
     [Vector Database\n(ChromaDB / Qdrant)] as VECTOR_DB
     [Graph Database\n(NetworkX / Neo4j)] as GRAPH_DB
   }

   package "Retrieval & Generation" as RAG {
     [Semantic\nRetriever] as RETRIEVER
     [Graph\nTraversal] as GRAPH_TRAV
     [Context\nAssembler] as ASSEMBLER
     [LLM\n(Claude API)] as LLM
   }

   package "User Interface" as UI {
     [CLI Q&A\nInterface] as CLI
     [REST API\n(FastAPI)] as API
   }

   RST --> PARSER
   PUML --> RENDERER
   JSON --> LOADER
   PARSER --> CHUNKER
   LOADER --> CHUNKER
   CHUNKER --> TEXT_EMB
   RENDERER --> IMG_EMB
   TEXT_EMB --> VECTOR_DB
   IMG_EMB --> VECTOR_DB
   JSON --> GRAPH_DB : requirement links\n(satisfies, derives_from, etc.)
   CLI --> RETRIEVER : user query
   API --> RETRIEVER : user query
   RETRIEVER --> VECTOR_DB : semantic search
   RETRIEVER --> GRAPH_TRAV : link traversal
   GRAPH_TRAV --> GRAPH_DB
   RETRIEVER --> ASSEMBLER : top-k results
   GRAPH_TRAV --> ASSEMBLER : related reqs
   ASSEMBLER --> LLM : context + query
   LLM --> CLI : answer + citations
   LLM --> API : answer + citations
   @enduml

----

Component Design
-----------------

Data Ingestion
~~~~~~~~~~~~~~

The ingestion pipeline extracts structured data from the requirements repository:

1. **Sphinx Build (needs.json):**

   .. code-block:: bash

      make needs
      # Output: build/needs/needs.json

   The ``needs.json`` file contains all requirement metadata (id, title, type,
   status, links, tags, content) in structured JSON format — ideal for RAG ingestion.

2. **RST Parser:** Uses ``docutils`` to parse RST files and extract text content
   per need item. Each need becomes one document chunk with its metadata.

3. **PlantUML Renderer:** Renders ``.puml`` files to PNG images for visual architecture
   understanding. Images are embedded alongside text in the vector database.

Text Embedding Strategy
~~~~~~~~~~~~~~~~~~~~~~~~

Each requirement is stored as an embedding with rich metadata:

.. code-block:: python

   # Document structure per requirement
   doc = {
       "id": "SYS_REQ_001",
       "title": "System shall monitor wheel speed at all four wheels",
       "content": "Full requirement text...",
       "type": "sys_req",
       "status": "approved",
       "safety_class": "ASIL-D",
       "aspice_process": "SYS.2",
       "satisfies": ["STKH_REQ_002"],
       "tags": ["sensing", "wheel-speed"],
       "embedding": [...]   # 384-dim sentence-transformers vector
   }

**Embedding model:** ``sentence-transformers/all-MiniLM-L6-v2``

- Dimension: 384
- Optimized for semantic similarity of technical text
- Fast inference (~50 ms per requirement on CPU)

Image Embedding Strategy
~~~~~~~~~~~~~~~~~~~~~~~~

Architecture diagrams (PlantUML rendered to PNG) are embedded using CLIP:

.. code-block:: python

   from PIL import Image
   import torch
   from transformers import CLIPProcessor, CLIPModel

   model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
   processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

   # Embed architecture diagram
   image = Image.open("Req/SYS3/diagrams/sys_component.png")
   inputs = processor(images=image, return_tensors="pt")
   image_features = model.get_image_features(**inputs)

Graph Database Design
~~~~~~~~~~~~~~~~~~~~~~

The graph database stores requirement relationships for traversal queries:

.. code-block:: python

   # NetworkX graph construction from needs.json
   import networkx as nx

   G = nx.DiGraph()

   for req in needs_data.values():
       G.add_node(req["id"], **req)

       # Add edges for each link type
       for linked_id in req.get("satisfies", []):
           G.add_edge(req["id"], linked_id, relation="satisfies")
       for linked_id in req.get("derives_from", []):
           G.add_edge(req["id"], linked_id, relation="derives_from")
       for linked_id in req.get("traces_to", []):
           G.add_edge(req["id"], linked_id, relation="traces_to")
       for linked_id in req.get("refines", []):
           G.add_edge(req["id"], linked_id, relation="refines")

   # Example traversal: find all SW_REQs for a STKH_REQ
   all_descendants = nx.descendants(G, "STKH_REQ_001")

RAG Query Pipeline
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Simplified RAG query pipeline
   from sentence_transformers import SentenceTransformer
   import chromadb
   import anthropic

   model = SentenceTransformer('all-MiniLM-L6-v2')
   client = chromadb.PersistentClient(path="./rag_db")
   collection = client.get_collection("abs_requirements")
   claude = anthropic.Anthropic()

   def query_requirements(user_question: str) -> str:
       # 1. Embed the user question
       query_vector = model.encode(user_question).tolist()

       # 2. Semantic retrieval from vector DB
       results = collection.query(
           query_embeddings=[query_vector],
           n_results=10,
           include=["documents", "metadatas", "distances"]
       )

       # 3. Build context from retrieved requirements
       context = "\n\n".join([
           f"[{meta['id']}] {meta['title']}\n{doc}"
           for doc, meta in zip(results['documents'][0], results['metadatas'][0])
       ])

       # 4. Generate answer with Claude
       response = claude.messages.create(
           model="claude-sonnet-4-5-20250929",
           max_tokens=1024,
           messages=[{
               "role": "user",
               "content": f"""You are an automotive requirements expert.
   Answer the following question based only on the provided requirements context.
   Always cite requirement IDs in your answer.

   Context:
   {context}

   Question: {user_question}"""
           }]
       )
       return response.content[0].text

----

Technology Stack
-----------------

+-------------------+------------------------------+----------------------------------+
| Component         | Technology                   | Purpose                          |
+===================+==============================+==================================+
| Text Embeddings   | sentence-transformers        | Semantic search over requirements|
+-------------------+------------------------------+----------------------------------+
| Image Embeddings  | CLIP (openai)                | Architecture diagram search      |
+-------------------+------------------------------+----------------------------------+
| Vector Database   | ChromaDB (local dev)         | Semantic similarity retrieval    |
|                   | Qdrant (production)          |                                  |
+-------------------+------------------------------+----------------------------------+
| Graph Database    | NetworkX (local dev)         | Requirement link traversal       |
|                   | Neo4j (production)           |                                  |
+-------------------+------------------------------+----------------------------------+
| LLM               | Claude (Anthropic API)       | Answer generation                |
|                   | Ollama (local, offline)      |                                  |
+-------------------+------------------------------+----------------------------------+
| RAG Framework     | LangChain / LlamaIndex       | Pipeline orchestration           |
+-------------------+------------------------------+----------------------------------+
| Requirement Export| sphinx-needs (needs.json)    | Structured data extraction       |
+-------------------+------------------------------+----------------------------------+
| API Server        | FastAPI                      | REST interface for Q&A           |
+-------------------+------------------------------+----------------------------------+

----

Implementation Roadmap
-----------------------

**Phase 1: Basic Text RAG (MVP)**

1. Run ``make needs`` to export ``needs.json``
2. Parse needs.json → embed with sentence-transformers
3. Store in ChromaDB locally
4. Simple CLI Q&A loop using Claude API

**Phase 2: Graph-Enhanced RAG**

1. Build NetworkX graph from requirement links
2. Hybrid retrieval: semantic + graph traversal
3. Provide link-traversal answers (e.g., "all SW requirements for STKH_REQ_001")

**Phase 3: Multi-Modal RAG**

1. Render PlantUML diagrams to PNG
2. Embed images with CLIP
3. Answer questions about architecture diagrams

**Phase 4: Production**

1. Migrate to Qdrant + Neo4j
2. FastAPI REST endpoint
3. Web UI with clickable requirement citations

----

Required Dependencies (Future)
--------------------------------

Uncomment these in ``requirements.txt`` when implementing:

.. code-block:: text

   chromadb>=0.4.0
   sentence-transformers>=2.2.2
   langchain>=0.1.0
   langchain-community>=0.0.10
   anthropic>=0.18.0
   Pillow>=10.0.0
   qdrant-client>=1.7.0
   networkx>=3.0
   fastapi>=0.104.0
   uvicorn>=0.24.0
   transformers>=4.35.0   # For CLIP
