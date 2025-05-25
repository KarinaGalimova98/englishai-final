# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite

all: stm2rttm.pl

stm2rttm.pl: 
	chmod +x stm2rttm.pl

check: all
	@echo "No Tests for stm2rttm.pl"

install: all
	cp stm2rttm.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
