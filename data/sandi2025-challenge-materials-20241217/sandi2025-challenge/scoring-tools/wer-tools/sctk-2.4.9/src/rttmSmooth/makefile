# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite

all: rttmSmooth.pl

rttmSmooth.pl: 
	chmod +x rttmSmooth.pl

check: all
	@echo "No Tests for rttmSmooth.pl"

install: all
	cp rttmSmooth.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
