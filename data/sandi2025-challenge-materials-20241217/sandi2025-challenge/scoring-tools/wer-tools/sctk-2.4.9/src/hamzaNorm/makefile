# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite

all: hamzaNorm.pl

hamzaNorm.pl: 
	chmod +x hamzaNorm.pl

setTests:
	cat $(T)/test.arb2004.txt | ./hamzaNorm.pl - $(T)/test.arb2004.hamzaNorm.txt
	cat $(T)/test.arb2004.txt.stm | sed 's/<O>//' | ./hamzaNorm.pl -i stm - $(T)/test.arb2004.txt.stm.hamza
	cat $(T)/test.arb2004.txt.ctm | ./hamzaNorm.pl -i ctm - - | sed 's/<O>//' > $(T)/test.arb2004.txt.ctm.hamza

check: all
	@echo "Testing hamzaNorm.pl"
	cat $(T)/test.arb2004.txt | ./hamzaNorm.pl -- - - | diff - $(T)/test.arb2004.hamzaNorm.txt
	cat $(T)/test.arb2004.txt.stm | sed 's/<O>//' | ./hamzaNorm.pl -i stm -- - - | diff - $(T)/test.arb2004.txt.stm.hamza
	cat $(T)/test.arb2004.txt.stm | ./hamzaNorm.pl -i stm -- - - | sed 's/<O>//' | diff - $(T)/test.arb2004.txt.stm.hamza
	cat $(T)/test.arb2004.txt.ctm | ./hamzaNorm.pl -i ctm -- - - | sed 's/<O>//' | diff - $(T)/test.arb2004.txt.ctm.hamza
	@echo "   hamzaNorm.pl tests successfully completed"

install: all
	cp hamzaNorm.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
