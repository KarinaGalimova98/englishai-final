# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite

all: csrfilt.sh

csrfilt.sh: 
	chmod +x csrfilt.sh

setTests:
	./RunTests.pl setTests

check: all
	@echo "Testing csrfilt.sh"
	./RunTests.pl
	@echo "   csrfilt.sh successfully completed"

install: all
	cp csrfilt.sh $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
