# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?= -W -j auto
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf "$(BUILDDIR)"
	rm -rf source/api/reference

livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)"/html $(SPHINXOPTS) $(O)

open:
	open "$(BUILDDIR)"/html/index.html

check:
	ruff check --select D,E501 ../eclypse

format:
	docformatter --in-place --recursive --wrap-summaries 88 --wrap-descriptions 88 ../eclypse

.PHONY: help clean livehtml open check format Makefile

# Catch-all target: route all unknown targets to Sphinx using make mode.
# $(O) is meant as a shortcut for extra Sphinx options.
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
