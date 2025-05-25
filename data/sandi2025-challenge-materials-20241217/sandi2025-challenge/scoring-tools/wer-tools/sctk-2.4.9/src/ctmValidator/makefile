SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin

all: ctmValidator.pl

rttmValidator.pl:
	chmod +x ctmValidator.pl

check: all
	(cd test_suite; $(SHELL) RunTest.sh ../ctmValidator.pl)

install: all
	cp ctmValidator.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
