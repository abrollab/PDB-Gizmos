#!/Users/erik/anaconda3/bin/python
############################################################
# The seedpicker algorthim will have a new data handler called the "sub long row processing"
# this will be proposed for the vesion 3 of seedpicker
# aim goal is to avoid out of memory erors 
# 
# This contains a new data handler known as smart sampling 
# This allow the creationg of the matrix by parts but also 
# gather the necesasry data in order to complete each phase 
############################################################
# standard package modules 
import os 
import sys
import argparse
import textwrap


# third party moduleπ
import numpy as np 
import pandas as pd 
import mdtraj as md

# pdbTools modules
from moltools.debugg.logger import Logger
from moltools.io.loader import iterload_by_group
from moltools.utils.rmsd import calculate_rmsd
from moltools.io.custom_args import ParseSelection
from moltools.io.infile_handler import parse_infile



def get_index(labled_trajs, tag, topology, group=None):
    """ creates the unique ID index and also flag to create index by group """
    
    



def seed_picker(labled_data, topfile, n_cores=4, stride=1, verbose=False, s_atoms=None):
    """ selects the best seeds based on RMSD. returns the average series """

    #-----------   
    # setting up
    #-----------
    logger = Logger('seedpicker.log')
    os.environ["OPM_NUM_THREADS"] = "{}".format(n_cores)    
    prmtop = md.load_topology(topfile)
    groups = [tag.spli('t')[0] for tag in labled_data.keys()] 

    logger.log_new_stage("Stage 1: selecting global outlier and solution structure")
    
        # get index column 
        
    # ---------------------------------------------------------
    # Stage 1: Looking for native outlier  
    # ---------------------------------------------------------
    for group in groups:
        selected_group = []
        loaded_traj = iterload_by_group(labled_data, prmtop, group)
        for tag in labled_data.keys():
            if tag.startswith(group):
                selected_group.append(tag)

        df_frames = []
        for group_trajs, merged_trjs in loaded_traj:
            for traj in group_trajs:                    
                rmsd = calculate_rmsd(traj, merged_trjs, stride=stride) # generator of 1D arrays 
                # creating a data frame for each trajobj in the group 
                rmsd_df = pd.DataFrame(rmsd)
                df_frames.append(rmsd_df)  
                    
        group_df = pd.concat(df_frames) # concatenates all df in the y direction 
        row_indx = get_index(labled_data, selected_group, prmtop) # gets the groups index 

        # TODO: (stopped here) create index functoin where it is able to produce the index columsn 
        # editing the column index and row index of the group dataframe 
        group_df.columns =
def help_message():
    """ Displays help message if the inputs are incorrect"""
    print(textwrap.dedent("""

        [Summary]
        Seedpicker.py is a brute-force algorithm that searches for a specific
        conformation that deviates greatly from other snapshots in a given
        trajectory.
        This program captures intrinsic and least populated conformations
        which could serve as aviable starting point to explore the
        conformational landscape.
        
        [Use Case Example]
        seedpicker.py -i traj_list.in -p 5g53_100ns_md.prmtop
        
        [Required arguments]:
        -i, --input             Input file containing all groupings of the
                                trajectories
        -t, --topology          The topology file prmtop
        
        [Optional arguments]:
        -c, --cores             Number of cores used for rmsd calculations
                                [default: 4]
        -s, --stride            Stide of frames that will be processed
                                [default: 1]
        -x, --cutoff            Cutoff value indicating if a new outlier is
                                found in the trajectories [default: 2.00]
        -o, --output            Write an output to the current directory. One
                                can select either matrix binary or csv. If
                                [Default: csv] [Choices: csv, matrix]
        -v, --verbose           Displays 20 lines of the rmsd data in each
                                stage
                                
        -r, --resids            Selection of residues that will be used for 
                                for RMSD calculations. If none is specified,
                                all atoms will be used for calcutions.
                                [default: None]
        -a, --atomtype          Refers to what atoms the user wants to use
                                when calculating for RMSD. 
                                [default: CA]
                                [choices: all, CA, backbone, sidechain, protein]
        """))
    sys.exit()


if __name__ == "__main__":
    
    # input parameters 
    if len(sys.argv) == 1:
        help_message()
    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        help_message()
    
    # CLI arguments  
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')
    required.add_argument('-i', '--input', type=str, required=True)
    required.add_argument('-t', '--topology', type=str, required=True)
    optional.add_argument('-c', '--cores', type=int, default=4, required=False)
    optional.add_argument('-s', '--stride', type=int, required=False, default=1)
    #optional.add_argument('-x', '--cutoff', type=float, required=False, default=2.00)
    optional.add_argument('-l', '--logger', type=str, required=False, default="seedpicker")
    optional.add_argument('-v', '--verbose', action='store_true', default=False, required=False)
    optional.add_argument('-r', '--resids', type=str, default=None, action=ParseSelection, required=False)
    optional.add_argument('-a', '--atomtype', type=str, default=None, choices=['all', 'CA', 'backbone', 'protein', 'sidechain'], required=False)
    args = parser.parse_args()
    
    # extracting data from 
    in_file = parse_infile(args.input)
    
