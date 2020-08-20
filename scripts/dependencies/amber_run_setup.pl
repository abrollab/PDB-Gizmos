#!/usr/bin/env perl

use warnings;

use FindBin (); 
use lib "$FindBin::Bin";
use Getopt::Long;
use File::Copy;
use File::Basename;
use Cwd;

GetOptions ('h|help'             => \$help,
            's|sysname=s'        => \$sysname,
            'r|resid=i'          => \$resid,
            );  

if (!$sysname || !$resid) { &help; }

print "Preparing input files for 6 Amber MD steps for $sysname\n";

$sbin = "$FindBin::Bin";
$cdir = cwd();

$s1="system"; $r1="$sysname";
$s2="RRR"; $r2="$resid";

@stepfiles = <$sbin/step*>; 
foreach $stepfile (@stepfiles) {
    ($filename,$dirname,my $suffix)=fileparse("$stepfile");
    $sysstepfile="$sysname"."_"."$filename";
    $sysfile="$cdir/$sysstepfile";
    # open the input file for reading
    open(I, "< $stepfile");
    # open a new input file, with system's name in it
    open(O, "> $sysfile");
    # go through the input file, replacing resid strings
    while(<I>) { $_ =~ s/$s2/$r2/g; print O $_; }
    # close files
    close(I);
    close(O);
}

#create bash scripts
$tp1file="$sbin/amberMD_phase1.template.bash";
$tp2file="$sbin/amberMD_phase2.template.bash";
$sp1file="$cdir/$sysname"."_amberMD_phase1.bash";
$sp2file="$cdir/$sysname"."_amberMD_phase2.bash";

open(I, "< $tp1file"); open(O, "> $sp1file");
while(<I>) { $_ =~ s/$s1/$r1/g; print O $_; }
close(I); close(O);
open(I, "< $tp2file"); open(O, "> $sp2file");
while(<I>) { $_ =~ s/$s1/$r1/g; print O $_; }
close(I); close(O);

system("chmod 755 $sp1file");
system("chmod 755 $sp2file");

#create PBS scripts
$tp1file="$sbin/amberMD_phase1.template.pbs";
$tp2file="$sbin/amberMD_phase2.template.pbs";
$sp1file="$cdir/$sysname"."_amberMD_phase1.pbs";
$sp2file="$cdir/$sysname"."_amberMD_phase2.pbs";

open(I, "< $tp1file"); open(O, "> $sp1file");
while(<I>) { $_ =~ s/$s1/$r1/g; print O $_; }
close(I); close(O);
open(I, "< $tp2file"); open(O, "> $sp2file");
while(<I>) { $_ =~ s/$s1/$r1/g; print O $_; }
close(I); close(O);

system("chmod 755 $sp1file");
system("chmod 755 $sp2file");

sub help {
    $help_message = "

<Program>
 = amber_run_setup.pl

<Release>
 = Version 1.1 (25 Jan 2015)

<Author(s)>
 = Ravi Abrol (abrolr\@csmc.edu)

<Program Options>
 : -h | --help             :: Optional    :: No Input
 : Prints this help message.

 : -s | --sysname         :: Required    :: String
 : This is the protein/ligand system name to be used as a prefix
   to identify for all the Amber MD files for your system.

 : -r | --resid          :: Required    :: Integer
 : This is the last residue ID that needs to be kept constrained during
   first few stages of MD. Usually this is the last residue of the protein/
   ligand system before the solvent.

Example:
    After you create an Amber MD folder for your system, e.g., p53,
    with files p53_md.inpcrd and p53_md.prmtop, then run the following
    command in that folder:
        amber_run_setup.pl -s p53 -r 298

    This will create 2 bash scripts:
        p53_amberMD_phase1.bash
        p53_amberMD_phase2.bash
    and six input files:
        p53_step1_mini_solv.in: 2000 steps of solvent minimization
        p53_step2_equi_solv.in: 250ps of solvent equilibration
        p53_step3_mini_full.in: 2000 steps of full system minimization
        p53_step4_heat_full.in: 100ps of heating system from 0 to 310.15K
        p53_step5_equi_full.in: 250ps of full system equilibration
        p53_step6_prod_full.in: 50ns of full system production

     Change any parameters that you may need for special situations.

     Run the p53_amberMD_phase1.bash script first, which will run steps 1-5.
     
     Do density/volume/energy analysis to make sure that the system is
     equilibrated.

     Then, run p53_amberMD_phase2.bash script, which will run the step 6 or
     production run.


";
    die $help_message;
}
