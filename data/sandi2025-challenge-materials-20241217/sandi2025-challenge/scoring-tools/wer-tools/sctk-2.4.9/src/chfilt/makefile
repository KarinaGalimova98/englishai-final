# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX=/home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
T=../test_suite

all: chfilt.pl

chfilt.pl: 
	chmod +x chfilt.pl

setTests:
	./chfilt.pl -m -l english $(T)/testmss.in -- - > $(T)/testmss.stm
	./chfilt.pl -C numbers -m -l english $(T)/testmss.in -- - > $(T)/testmss.numbers.stm
	./chfilt.pl -l english -i -b 0 -e 999999 -k $(T)/test.txt -- - > $(T)/test.txt.-optdel.stm
	./chfilt.pl -d -l english -i -b 0 -e 999999 -k $(T)/test.txt -- - > $(T)/test.txt.stm
	./chfilt.pl -c -l english -i -b 0 -e 999999 -k $(T)/test.txt -- - > $(T)/test.txt.-contexp.stm
	./chfilt.pl -c -l arabic -i -b 0 -e 999999 -d -k $(T)/test.arb2004.txt -- - > $(T)/test.arb2004.txt.stm
	./chfilt.pl -c -l mandarin -i -b 0 -e 999999 -d -k $(T)/test.man2004.txt -- - > $(T)/test.man2004.txt.stm

check: all
	@echo "Testing chfilt.pl"
	./chfilt.pl -m -l english $(T)/testmss.in -- - | diff - $(T)/testmss.stm
	./chfilt.pl -C numbers -m -l english $(T)/testmss.in -- - | diff - $(T)/testmss.numbers.stm
	./chfilt.pl -l english -i -b 0 -e 999999 -k $(T)/test.txt -- - | diff - $(T)/test.txt.-optdel.stm
	./chfilt.pl -d -l english -i -b 0 -e 999999 -k $(T)/test.txt -- - | diff - $(T)/test.txt.stm
	./chfilt.pl -c -l english -i -b 0 -e 999999 -k $(T)/test.txt -- - | diff - $(T)/test.txt.-contexp.stm	
	./chfilt.pl -c -l arabic -i -b 0 -e 999999 -d -k $(T)/test.arb2004.txt -- - | diff - $(T)/test.arb2004.txt.stm
	./chfilt.pl -c -l mandarin -i -b 0 -e 999999 -d -k $(T)/test.man2004.txt -- - | diff - $(T)/test.man2004.txt.stm
	@echo "   chfilt.pl tests successfully completed"

install: all
	cp chfilt.pl $(bindir)

clean:

distclean: clean
	rm -r *~ makefile
