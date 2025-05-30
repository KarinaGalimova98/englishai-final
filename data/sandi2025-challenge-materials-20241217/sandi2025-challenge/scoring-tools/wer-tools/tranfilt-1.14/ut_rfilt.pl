#!/usr/local/bin/perl


#
#  File   ut_rfilt.pl
#  Date:  Jan 31, 1994
#  Usage: ut_rfilt rule_file input_file output_file
#  
#  Desc:  This program takes a filter file similar to that of rfilter1xx
#         except that an utterance id, which the rule is to be applied to,
#         is listed after the text conversion rule.  The program first
#         reads the rule file, setting up a associative array of rules
#         based on the utterance id's.  The program then reads each line
#         from the transcript file.  If the utterance does not have a rule
#         to apply, it is written out without modification.  Otherwise,
#         the rules is applied to the sentence, and the outcome written
#         to the output file.
#          
#  Version 1.0 Feb 1, 1993
#  version 1.1 Oct 20, 1995
#      Made the program pass through comment lines unchanged
#

Version="1.1";

# Change to the installation directory in order to execute from 
# any where other than the installation directory.
$EXE_DIR="/home/bluec/babel/NIST/tranfilt-1.14";

# define an associative array
%ref_trans=();

#
#
##
# Parse the header arguements
#
@argv=();
if ($#ARGV != 2) {
       	&perr_usage("Not enough arguments, 3 expected");
}
else {
	$RULE_FILE = $ARGV[$i++];
        $TRANSCRIPT = $ARGV[$i++];
        $OUT_FILE = $ARGV[$i];
}

if (($RULE_FILE =~ /^$/) || ($TRANSCRIPT =~ /^$/) || ($OUT_FILE =~ /^$/)){
	&perr_usage("I need a rule, transcripts and out\n");
}


#
# Read in the rule file, setting up an associative array
#
if(!open(FILE,$RULE_FILE)){
         &perr("cannot open the RULE file $RULE_FILE"); 
}
while (<FILE>){
        if ($_ =~ /^;;/ || $_ =~ /^\*/){
                ;  #skip the comment line
	} else {  # 
		chop;
		s/ *$//;
		tr/a-z/A-Z/;
		($id = $_) =~ s/^.*-> *//;
		($rule = $_) =~ s/->.*$//;
		if ($ref_trans{$id}  =~ /^$/){
			$ref_trans{$id} = $rule;
		} else {
			$ref_trans{$id} = "$ref_trans{$id}\n$rule";
		}
		# print "UTT $id 	rule $rule \n";
	}
}
close(FILE);

#
# open the input transcription file
if(!open(FILE,$TRANSCRIPT)){
         &perr("cannot open the LSN file $TRANSCRIPT"); 
}

#
# open the output file
if(!open(OUTFILE,">$OUT_FILE")){
         &perr("cannot open the OUTPUT file $OUT_FILE"); 
}

#
# Process each transcription
while (<FILE>){
        if ($_ =~ /^;;/){
                print;
        } else {  # 
		chop;
		($id = $_) =~ s/^.*\(([^()]*)\)\s+$/\1/;
		if ($ref_trans{$id}  =~ /^$/){
			print OUTFILE "$_\n";
		} else {
			# open a temp file for the transcript
			if(!open(TMPF,">/tmp/perl.utt.$$")){
			         &perr("cannot open the temp file $/tmp/perl.utt.$$");
			}
			# write out the transcript
			print TMPF "$_\n";
			# close the file
			close(TMPF);

			# open a temporary file for the rule file
			if(!open(TMPF,">/tmp/perl.scr.$$")){
			         &perr("cannot open the temp file $/tmp/perl.scr.$$");
			}
			print TMPF ";; File tmp_special.rls\n";
			print TMPF ";; Rules for mapping one lexical equivalent to another,\n";
			print TMPF ";; used in CSR test January 1994.\n";
			print TMPF ";; (Applies to .lsn, not .dot)\n";
			print TMPF "* name \"map1\"\n";
			print TMPF "* desc \"Selective map\"\n";
			print TMPF "* copy_no_hit = \'T\'\n";
			print TMPF "$ref_trans{$id}\n";
			close(TMPF);

			# open a process to filter the data
			if(!open(TMPF,"$EXE_DIR/rfilter1 /tmp/perl.scr.$$ < /tmp/perl.utt.$$ | ")){
			         &perr("cannot open the filter files");
			}
			
			while (<TMPF>){
				print OUTFILE $_;
			}
			close(TMPF);
		}
	}
}
close(FILE);


sub usage
{
        print "Usage: perl_filter_utt rules transcripts outputfile\n";
}

sub perr
{       print STDERR "Error: $_[0]\n";
        exit(1);
}
 
sub perr_usage
{       print STDERR "Error: $_[0]\n";
        &usage;
        exit(1);
}

