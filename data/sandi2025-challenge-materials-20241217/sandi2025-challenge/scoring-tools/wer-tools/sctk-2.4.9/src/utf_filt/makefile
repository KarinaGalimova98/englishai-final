# **********************************************************
# Makefile for rfilter1 Directory
# **********************************************************
SHELL = /bin/sh
PREFIX = /home/bluec/babel/NIST/sctk-2.4.9
bindir = $(PREFIX)/bin
NSGMLS = 
T=../test_suite

all: utf_filt.pl

utf_filt.pl: 
	chmod +x utf_filt.pl

setTests:
	utf_filt.pl -e utf-1.2.dtd -f stm -i ../test_suite/test.man.utf -o ../test_suite/test.man.stm -d

check: all
	@echo "Testing utf_filt.pl"
	@-if test "$(NSGMLS)" = "" ; then \
		echo "!!!!  Skipping Tests because NSGMLS is not installed  !!!!"; \
	else \
		perl utf_filt.pl -s $(NSGMLS) -e utf-1.2.dtd -f stm -i ../test_suite/test.man.utf -o - -d | diff - ../test_suite/test.man.stm; \
		perl utf_filt.pl -s $(NSGMLS) -e utf-1.2.dtd -f stm -i ../test_suite/test.eng.utf -o - -d | diff - ../test_suite/test.eng.stm; \
		perl utf_filt.pl -s $(NSGMLS) -t -n -e utf-1.2.dtd -f stm -i ../test_suite/test.eng.utf -o - -d | diff - ../test_suite/test.eng.notrans.stm; \
	fi	

install: all
	@sed 's:"nsgmls":"'$(NSGMLS)'":' < utf_filt.pl > $(bindir)/utf_filt.pl
	@chmod +x $(bindir)/utf_filt.pl

config.sh: config.in
	autoconf config.in | sed 's/Makefile/makefile/g' > config.sh

# config.status might not change config.h, but it changes stamp-h.
makefile: makefile.in config.status
	./config.status

clean:

distclean: clean
	rm -r *~ makefile
