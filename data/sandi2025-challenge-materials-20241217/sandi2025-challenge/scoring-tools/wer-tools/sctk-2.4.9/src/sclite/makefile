# Generated automatically from makefile.in by configure.
# makefile for SCLITE

#### Start of system configuration section. ####

srcdir = .

CC = gcc
INSTALL = /usr/bin/install

GNUDIFF = 
CPPFLAGS = 
DEFS =  -DHAVE_LIBM=1 -DSTDC_HEADERS=1 -DHAVE_UNISTD_H=1 
CFLAGS = -Os
LDFLAGS = 
SLM_TARGETS = 
LIBS = -lm  $(SLM_TARGETS)

# Some System V machines do not come with libPW.
# If this is true for you, use the GNU alloca.o here.

prefix = /home/bluec/babel/NIST/sctk-2.4.9
exec_prefix = ${prefix}
edit_program_name = sed 's,x,x,'

bindir = $(exec_prefix)/bin
mandir =$(prefix)/man
man1dir =$(mandir)/man1
man5dir = $(mandir)/man5

infodir = $(prefix)/info

DEFAULT_EDITOR_PROGRAM = ed
NULL_DEVICE = /dev/null
PR_PROGRAM = /bin/pr

#### End of system configuration section. ####

SHELL = /bin/sh

######################################################################
# The source files for all of the programs.
glib_c = order.c rsprintf.c path.c text.c scores.c word.c rpg.c statdist.c \
	pad.c sgml.c readpipe.c alex.c sc_dtl.c det.c wwscr_f.c corresp.c \
	slm_intf.c

statlib_c = rank.c range.c anovar.c signtest.c wilcoxon.c sentmcn.c mtchprs.c 

netlib_c = addarc1.c delarc1.c llist.c marc1.c arcseq1.c \
	mnode1.c boolpr1.c killarc1.c net_adt.c knode2.c net_dp.c 

align_c = stm.c align.c dwtoke2.c fillmrks.c wtokeini.c lur.c stm2ctm.c \
	ctm2ctm.c mfa.c cores.c


######################################################################
# The Object files for all of the library code.
glib_o = order.o rsprintf.o path.o text.o scores.o word.o rpg.o statdist.o \
	pad.o sgml.o readpipe.o alex.o sc_dtl.o det.o wwscr_f.o corresp.o \
	slm_intf.o

statlib_o = rank.o range.o anovar.o signtest.o wilcoxon.o sentmcn.o mtchprs.o 

netlib_o = addarc1.o delarc1.o llist.o marc1.o arcseq1.o \
	mnode1.o boolpr1.o killarc1.o net_adt.o knode2.o net_dp.o 

align_o = stm.o align.o dwtoke2.o fillmrks.o wtokeini.o lur.o stm2ctm.o \
	ctm2ctm.o mfa.o cores.o

######################################################################
#  Group the libraries into their seperate forms either standalone or
#  in the tool kit

sclib_c = $(glib_c) $(netlib_c) $(align_c)
tklib_c = $(sclib_c) $(statlib_c)

sclib_o = $(glib_o) $(netlib_o) $(align_o)
tklib_o = $(sclib_o) $(statlib_o)

SC_PROGRAMS = sclite
TK_PROGRAMS = $(SC_PROGRAMS) sc_stats rover sctkUnit

TEST_PROGRAMS =  test test2 sc_conf mtchpath rover_v2 sc_quick mprint

PURIFY_PROGRAMS = $(PROGRAMS:%=%_pure) $(TEST_PROGRAMS:%=%_pure)

PURECOV_PROGRAMS = $(PROGRAMS:%=%_purecov)

DOCS = ../install.txt ../readme.txt ../disclaim.txt ../revision.txt \
	../makefile ../doc 
CONFIG = makefile.in config.sh config.in config.txt

tk_distfiles = $(tklib_c) $(TK_PROGRAMS:%=%.c) *.h $(CONFIG) testdata 

######################################################################
###############   Defines the installation type  #####################
lib_o = $(tklib_o)
lib_c = $(tklib_c)
PROGRAMS = $(TK_PROGRAMS)
distribution = tk_dist

#lib_o = $(sclib_o)
#lib_c = $(sclib_c)
#PROGRAMS = $(SC_PROGRAMS)
#distribution = sc_dist

######################################################################


all: makefile $(SLM_TARGETS) $(PROGRAMS)


COMPILE = $(CC) -c $(CPPFLAGS) $(DEFS) -I. $(CFLAGS)

.c.o:
	$(COMPILE) $<

sclite: $(lib_o) sclite.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) sclite.c $(LIBS) 
sc_stats: $(lib_o) sc_stats.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) sc_stats.c $(LIBS) 
rover: $(lib_o) rover.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) rover.c $(LIBS) 
mcnemar: $(lib_o) mcnemar.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) mcnemar.c $(LIBS)
sctkUnit: $(lib_o)sctkUnit.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) sctkUnit.c $(LIBS) 
sign: $(lib_o) sign.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) sign.c $(LIBS)
sclite_tolower: $(lib_o) sclite_tolower.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) sclite_tolower.c $(LIBS)
$(TEST_PROGRAMS): $(lib_o) $$@.c
	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) $@.c $(LIBS) 
$(PURIFY_PROGRAMS): $(lib_o)
	purify $(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) `echo $@.c|sed 's/_pure//'` $(LIBS) 
$(PURECOV_PROGRAMS): $(lib_o)
	purecov $(CC) -o $@ $(CFLAGS) $(LDFLAGS) $(lib_o) `echo $@.c|sed 's/_purecov//'` $(LIBS) 

### make a rule to compile the SLM toolkit
slm_v2/lib/SLM2.a:
	(cd slm_v2/src; make SLM2.a install-lib)

#arpg: rpg.o arpg.o pad.o 
#	$(CC) -o $@ $(CFLAGS) $(LDFLAGS) rpg.o arpg.o pad.o $(LIBS)
clean:
	rm -f *.o $(PROGRAMS) core
	if test -f slm_v2/src/makefile ; then \
		(cd slm_v2/src; make spotless) \
	fi

mostlyclean: clean

distclean: clean
	rm -rf *~ config.status config.log config.cache config.h makefile

realclean: distclean
	rm -f TAGS *.info*

install: all testinstalldirs
	for p in $(PROGRAMS); do \
	  $(INSTALL) $$p $(bindir)/$$p; \
	done
#REenable this later
#	for p in `(cd ../doc ; ls *.1)`; do \
#	  $(INSTALL) ../doc/$$p $(man1dir)/$$p; \
#	done
#	@echo "!!!!  If 'man sclite' does not work, run 'catman -M $(mandir)'"
#	@echo "!!!!  to make manual pages accessible."

testinstalldirs:
	@-for p in $(bindir) $(man1dir) $(man5dir); do \
	   if test ! -d $$p ; then \
		echo "Error: directory $$p doesn't exist"; \
	   fi ; \
#REenable this later
#	   if test ! -w $$p ; then \
#		echo "Error: directory $$p is not writeable by you"; \
#	   fi \
	done

# We need more tests.
check: sctkUnit
	./sctkUnit
	cd testdata && ./tsclite.sh
	cd testdata && ./tsc_stats.sh

uninstall:
	for p in $(PROGRAMS); do \
	  rm -f $(bindir)/`echo $$p | $(edit_program_name)`; \
	done
	for p in `(cd ../doc ; ls *.1)`; do \
	  rm -f $(man1dir)/$$p; \
	done

config.sh: config.in
	cd $(srcdir) && /usr/local/bin/autoconf config.in | sed 's/Makefile/makefile/g' > config.sh

# autoheader might not change config.hin.
config.hin: stamp-h.in
stamp-h.in: config.in
	cd $(srcdir) && autoheader
	date > $(srcdir)/stamp-h.in

config.status: config.sh
	./config.status --recheck

# config.status might not change config.h, but it changes stamp-h.
makefile: makefile.in config.status
	./config.status

dist: $(distribution)

tk_dist: $(tk_distfiles)
	echo sctk-`grep define\ TK_VERSION sctk.h | sed -e 's/^[^"]*"//' -e 's/"[^"]*//'` > .fname
	echo "Distribution file '../`cat .fname`.tar.Z'"
	(cd ../doc; ./export.sh $(PROGRAMS))
	rm -rf ../`cat .fname`
	mkdir ../`cat .fname`
	(cd ./testdata; tsclite.sh -clean) ;
	for file in $(DOCS); do \
		ln -s $$file ../`cat .fname`; \
	done
	mkdir ../`cat .fname`/src
	for file in $(tk_distfiles); do \
		ln -s ../../src/$$file ../`cat .fname`/src/$$file; \
	done
	echo "Installing SLM links"
	mkdir ../`cat .fname`/src/slm_v2
	mkdir ../`cat .fname`/src/slm_v2/lib
	mkdir ../`cat .fname`/src/slm_v2/bin
	mkdir ../`cat .fname`/src/slm_v2/src
	for file in readme.txt endian.sh include doc; do \
		ln -s ../../../src/slm_v2/$$file ../`cat .fname`/src/slm_v2/$$file; \
	done
	echo "    Copying SLM source"
	tar cf - `find slm_v2/src \( -name makefile.in -o -name install-sh -o -name "*.[ch]" \) -print` | (cd ../`cat .fname`/src; tar xf -)
	echo "Tar-ing SLM to make it ISO-compatable"
	(cd ../`cat .fname`/src; tar chf slm_v2.tar ./slm_v2; rm -r slm_v2)
	(cd .. ; tar -chf - --exclude=CVS `cat src/.fname` | compress > `cat src/.fname`.tar.Z)
	rm -rf ../`cat .fname`
	echo "Decompressing the release file"
	(cd .. ; zcat `cat src/.fname`.tar.Z | tar xf -)
	echo "ISO_checking.   . . . Only the top-level makefile should fail"
	(cd ..; iso_check `cat src/.fname`)
	rm -rf ../`cat .fname` .fname

# Prevent GNU make v3 from overflowing arg limit on SysV.
.NOEXPORT:
