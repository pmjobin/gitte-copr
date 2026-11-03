# COPR SCM configuration: select "make srpm" (not rpkg).
# COPR invokes this with `make -f .copr/Makefile srpm outdir=... spec=...`.
# Network access is used only in this SRPM-production stage.

spec ?= gitte.spec
outdir ?= $(CURDIR)/_srpms

SPECFILE := $(abspath $(spec))
OUTDIR := $(abspath $(outdir))
SOURCEDIR := $(OUTDIR)/sources

.PHONY: srpm
srpm:
	dnf -y install cargo rust cargo-rpm-macros rpm-build git-core ca-certificates curl tar gzip xz
	@set -eu; \
	  version="$$(rpmspec -q --srpm --qf '%{VERSION}\n' '$(SPECFILE)')"; \
	  test -n "$$version"; \
	  printf 'Preparing Gitte %s with vendored Rust sources for COPR...\n' "$$version"; \
	  mkdir -p '$(SOURCEDIR)' '$(OUTDIR)'; \
	  bash ./make-gitte-vendor.sh "$$version" '$(SOURCEDIR)'; \
	  test -s '$(SOURCEDIR)/'"$$version"'.tar.gz'; \
	  test -s '$(SOURCEDIR)/gitte-'"$$version"'-vendor.tar.xz'; \
	  rpmbuild -bs \
	    --define '_sourcedir $(SOURCEDIR)' \
	    --define '_srcrpmdir $(OUTDIR)' \
	    '$(SPECFILE)'
