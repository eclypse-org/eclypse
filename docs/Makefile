# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

clean:
	rm -rf $(BUILDDIR)
	rm -rf source/api/reference

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

livehtml: clean
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)"/html $(SPHINXOPTS) $(O)

# check docstrings using pylint in ../eclypse module
check:
	pylint --rcfile=../.pylintrc --enable=C0114,C0115,C0116 --disable=R0801,E0611 ../eclypse

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile clean
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
