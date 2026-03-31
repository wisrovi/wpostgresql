# Makefile for Sphinx documentation
# Compatible with local development and ReadTheDocs

.PHONY: help html clean serve livehtml devhelp dirhtml singlehtml gettext doctest coverage check

# Custom variables
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

# ReadTheDocs environment variables
READTHEDOCS_OUTPUT ?= $(BUILDDIR)/html
READTHEDOCS_LANGUAGE ?= en

help:
	@echo "Available targets:"
	@echo "  html        - Build HTML documentation (default)"
	@echo "  dirhtml     - Build HTML directory index"
	@echo "  singlehtml  - Build single HTML file"
	@echo "  gettext     - Build gettext files"
	@echo "  devhelp     - Build HTML with development help"
	@echo "  clean       - Remove build artifacts"
	@echo "  serve       - Build and serve locally on port 8000"
	@echo "  livehtml    - Build with auto-reload on changes"
	@echo "  doctest     - Run doctests"
	@echo "  check       - Check links and syntax"

# Default: Build HTML
html: $(BUILDDIR)/html

$(BUILDDIR)/html:
	$(SPHINXBUILD) -b html -T -j auto -d $(BUILDDIR)/doctrees -D language=$(READTHEDOCS_LANGUAGE) . $(READTHEDOCS_OUTPUT)

# Single HTML file
singlehtml: $(BUILDDIR)/singlehtml

$(BUILDDIR)/singlehtml:
	$(SPHINXBUILD) -b singlehtml -T -j auto -d $(BUILDDIR)/doctrees . $(BUILDDIR)/singlehtml

# Directory HTML
dirhtml: $(BUILDDIR)/dirhtml

$(BUILDDIR)/dirhtml:
	$(SPHINXBUILD) -b dirhtml -T -j auto -d $(BUILDDIR)/doctrees . $(BUILDDIR)/dirhtml

# Gettext (internationalization)
gettext:
	$(SPHINXBUILD) -b gettext -d $(BUILDDIR)/doctrees . $(BUILDDIR)/gettext

# Development help
devhelp:
	$(SPHINXBUILD) -b html -T -j auto -d $(BUILDDIR)/doctrees -D language=$(READTHEDOCS_LANGUAGE) . $(BUILDDIR)/html -A devhelp=1

# Clean build artifacts
clean:
	rm -rf $(BUILDDIR)
	rm -rf .doctrees
	rm -rf _static
	rm -rf _templates

# Serve locally
serve: html
	@echo "Serving documentation at http://localhost:8000"
	@python -m http.server 8000 -d $(READTHEDOCS_OUTPUT)

# Live reload (requires sphinx-autobuild)
livehtml:
	sphinx-autobuild -b html -T -j auto -d $(BUILDDIR)/doctrees . $(BUILDDIR)/html

# Doctests
doctest:
	$(SPHINXBUILD) -b doctest -d $(BUILDDIR)/doctrees . $(BUILDDIR)/doctest

# Coverage report
coverage:
	$(SPHINXBUILD) -b coverage -d $(BUILDDIR)/doctrees . $(BUILDDIR)/coverage

# Link checker
check:
	sphinx-build -b linkcheck -d $(BUILDDIR)/doctrees . $(BUILDDIR)/linkcheck

.PHONY: $(BUILDDIR)/html $(BUILDDIR)/singlehtml $(BUILDDIR)/dirhtml