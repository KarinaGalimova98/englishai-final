SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin

all: align2html.pl

align2html.pl: align2html-main.pl buildInstallVersion.pl
	perl buildInstallVersion.pl > align2html.pl
	chmod +x align2html.pl

check: all
	@echo "No Tests for align2html.pl"

install: all
	perl buildInstallVersion.pl > $(bindir)/align2html.pl
	chmod +x $(bindir)/align2html.pl

buildPackFile:
	buildPack.pl > packImageTarFile

clean:

distclean: clean
	rm -r *~ makefile
