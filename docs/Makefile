# Makefile for Sphinx documentation

.PHONY: html clean serve livehtml help

help:
	@echo "Available targets:"
	@echo "  html      - Build HTML documentation"
	@echo "  clean     - Remove built documentation"
	@echo "  serve     - Build and serve documentation locally"
	@echo "  livehtml  - Build with auto-reload on changes (requires sphinx-autobuild)"

html:
	sphinx-build -b html . _build/html

clean:
	rm -rf _build
	rm -rf _templates
	rm -rf .doctrees

serve: html
	@echo "Serving documentation at http://localhost:8000"
	@python -m http.server 8000 -d _build/html

livehtml:
	sphinx-build -b html . _build/html -W --watch . --open-browser