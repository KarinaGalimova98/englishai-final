# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite

all: tanweenFilt.pl

tanweenFilt.pl: 
	chmod +x tanweenFilt.pl

setTests:
	cat $(T)/test.arb2004.txt | ./tanweenFilt.pl - $(T)/test.arb2004.tanweenFilt.txt
	cat $(T)/test.arb2004.txt.stm | sed 's/<O>//' | ./tanweenFilt.pl -i stm - $(T)/test.arb2004.txt.stm.tanween
	cat $(T)/test.arb2004.txt.ctm | ./tanweenFilt.pl -i ctm - - | sed 's/<O>//' > $(T)/test.arb2004.txt.ctm.tanween
	cat $(T)/test.arb2004.txt | ./tanweenFilt.pl -a - $(T)/test.arb2004.tanweenFilt-a.txt
	cat $(T)/test.arb2004.txt.stm | sed 's/<O>//' | ./tanweenFilt.pl -a -i stm - $(T)/test.arb2004.txt.stm.tanween-a
	cat $(T)/test.arb2004.txt.ctm | ./tanweenFilt.pl -a -i ctm - - | sed 's/<O>//' > $(T)/test.arb2004.txt.ctm.tanween-a

check: all
	@echo "Testing tanweenFilt.pl"
	cat $(T)/test.arb2004.txt | ./tanweenFilt.pl -- - - | diff - $(T)/test.arb2004.tanweenFilt.txt
	cat $(T)/test.arb2004.txt | ./tanweenFilt.pl -a -- - - | diff - $(T)/test.arb2004.tanweenFilt-a.txt
	cat $(T)/test.arb2004.txt.stm | sed 's/<O>//' | ./tanweenFilt.pl -i stm -- - - | diff - $(T)/test.arb2004.txt.stm.tanween
	cat $(T)/test.arb2004.txt.stm | ./tanweenFilt.pl -i stm -- - - | sed 's/<O>//' | diff - $(T)/test.arb2004.txt.stm.tanween
	cat $(T)/test.arb2004.txt.stm | ./tanweenFilt.pl -a -i stm -- - - | sed 's/<O>//' | diff - $(T)/test.arb2004.txt.stm.tanween-a
	cat $(T)/test.arb2004.txt.ctm | ./tanweenFilt.pl -i ctm -- - - | sed 's/<O>//' | diff - $(T)/test.arb2004.txt.ctm.tanween
	cat $(T)/test.arb2004.txt.ctm | ./tanweenFilt.pl -a -i ctm -- - - | sed 's/<O>//' | diff - $(T)/test.arb2004.txt.ctm.tanween-a
	@echo "   tanweenFilt.pl tests successfully completed"

install: all
	cp tanweenFilt.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
