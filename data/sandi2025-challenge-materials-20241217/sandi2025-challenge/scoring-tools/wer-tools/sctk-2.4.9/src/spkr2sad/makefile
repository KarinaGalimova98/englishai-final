# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite

all: spkr2sad.pl

spkr2sad.pl: 
	chmod +x spkr2sad.pl

check: all
	@echo "No Tests for spkr2sad.pl"

install: all
	cp spkr2sad.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
