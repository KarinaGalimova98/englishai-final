# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite
PERL=/slp/sware/Linux/bin/perl

all: hubscr.pl

hubscr.pl: 
	chmod +x hubscr.pl

setTests:
	./RunTests.pl setTests

check: all
	@echo "Testing hubscr.pl"
	./RunTests.pl
	@echo "   hubscr.pl tests successfully completed"

install: all
	cp hubscr.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
