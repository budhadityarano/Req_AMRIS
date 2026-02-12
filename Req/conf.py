# Configuration file for the Sphinx documentation builder.
# ABS Requirements - ASPICE-Compliant Automotive Software Requirements
# Process Areas: SYS.1, SYS.2, SYS.3, SWE.1, SWE.2, SWE.3

import os
import sys

# -- Project information -------------------------------------------------------
project = 'ABS Requirements - ASPICE'
copyright = '2024, ABS Development Team'
author = 'ABS Development Team'
release = '1.0.0'

# -- General configuration -----------------------------------------------------
extensions = [
    'sphinx_needs',
    'sphinxcontrib.plantuml',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- HTML output ---------------------------------------------------------------
html_theme = 'furo'
html_title = 'ABS Requirements Specification - ASPICE'
html_static_path = ['_static']

# -- PlantUML Configuration ----------------------------------------------------
# Option 1: PlantUML installed via brew/apt (recommended)
#   macOS:  brew install plantuml
#   Ubuntu: sudo apt-get install plantuml
plantuml = 'plantuml'

# Option 2: PlantUML .jar file (uncomment and set path)
# plantuml = 'java -jar /usr/local/lib/plantuml.jar'

plantuml_output_format = 'png'

# -- Sphinx-Needs Configuration ------------------------------------------------
# Need Types - ASPICE Process Areas (Left side of V-model only)
needs_types = [
    # SYS.1 - Stakeholder Requirements Analysis
    {
        "directive": "stkh_req",
        "title": "Stakeholder Requirement",
        "prefix": "STKH_REQ_",
        "color": "#E3F2FD",
        "style": "node",
    },
    # SYS.2 - System Requirements Analysis
    {
        "directive": "sys_req",
        "title": "System Requirement",
        "prefix": "SYS_REQ_",
        "color": "#BBDEFB",
        "style": "node",
    },
    # SYS.3 - System Architectural Design
    {
        "directive": "sys_arch",
        "title": "System Architecture",
        "prefix": "SYS_ARCH_",
        "color": "#90CAF9",
        "style": "artifact",
    },
    # SWE.1 - Software Requirements Analysis
    {
        "directive": "sw_req",
        "title": "Software Requirement",
        "prefix": "SW_REQ_",
        "color": "#C8E6C9",
        "style": "node",
    },
    # SWE.2 - Software Architectural Design
    {
        "directive": "sw_arch",
        "title": "Software Architecture",
        "prefix": "SW_ARCH_",
        "color": "#A5D6A7",
        "style": "artifact",
    },
    # SWE.3 - Software Detailed Design & Implementation
    {
        "directive": "sw_design",
        "title": "Software Detailed Design",
        "prefix": "SW_DESIGN_",
        "color": "#81C784",
        "style": "node",
    },
]

# ASPICE-Specific Traceability Link Types
needs_extra_links = [
    # sys_req SATISFIES stkh_req (system req satisfies stakeholder req)
    {
        "option": "satisfies",
        "incoming": "is satisfied by",
        "outgoing": "satisfies",
        "style": "bold",
        "color": "#1565C0",
    },
    # sys_arch/sw_req DERIVES_FROM higher-level req/arch
    {
        "option": "derives_from",
        "incoming": "derives to",
        "outgoing": "derives from",
        "style": "solid",
        "color": "#2E7D32",
    },
    # sw_req TRACES_TO system architecture element
    {
        "option": "traces_to",
        "incoming": "traced from",
        "outgoing": "traces to",
        "style": "dashed",
        "color": "#6A1B9A",
    },
    # sw_arch/sw_design REFINES higher-level architecture
    {
        "option": "refines",
        "incoming": "refined by",
        "outgoing": "refines",
        "style": "solid",
        "color": "#E65100",
    },
]

# ASPICE-specific metadata options on each need item
needs_extra_options = [
    "aspice_process",       # Which ASPICE process: SYS.1, SYS.2, SYS.3, SWE.1, SWE.2, SWE.3
    "safety_class",         # ASIL level: ASIL-A, ASIL-B, ASIL-C, ASIL-D, QM
    "verification_method",  # inspection, test, analysis, demonstration
    "priority",             # high, medium, low
    "rationale",            # justification for the requirement
]

# Requirement ID format validation
needs_id_regex = r'^[A-Z][A-Z0-9_]+$'
needs_id_required = True

# Link display options
needs_show_link_type = True
needs_show_link_title = True

# Export needs as JSON for RAG system ingestion
# Build with: make needs   (uses sphinx -b needs builder)
# Output: build/needs/needs.json
