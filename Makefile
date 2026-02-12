# Makefile for ABS Requirements Sphinx Documentation
# ASPICE-Compliant Automotive Requirements Management

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = Req
BUILDDIR      = build

.PHONY: help html needs clean install livehtml

help:
	@echo "Available targets:"
	@echo "  html      Build HTML documentation"
	@echo "  needs     Export needs.json (for RAG system)"
	@echo "  clean     Remove build artifacts"
	@echo "  install   Install Python dependencies"
	@echo "  livehtml  Start live-reload development server"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Python 3.9+ with pip"
	@echo "  - PlantUML: brew install plantuml (macOS)"
	@echo "             or: sudo apt-get install plantuml (Ubuntu)"
	@echo "  - Java (required by PlantUML)"

html:
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo ""
	@echo "Build finished. Open: $(BUILDDIR)/html/index.html"

needs:
	$(SPHINXBUILD) -b needs "$(SOURCEDIR)" "$(BUILDDIR)/needs" $(SPHINXOPTS)
	@echo ""
	@echo "Needs JSON exported to: $(BUILDDIR)/needs/needs.json"
	@echo "(Use this file as input to the RAG system)"

clean:
	rm -rf $(BUILDDIR)/*
	@echo "Build directory cleaned."

install:
	pip install -r requirements.txt

livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
