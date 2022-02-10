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
from pdb_gizmpos.debugg.logger import Logger
from pdb_gizmpos.io.loader import iterload_by_group
from pdb_gizmpos.utils.rmsd import calculate_rmsd
from pdb_gizmpos.io.custom_args import ParseSelection
from pdb_gizmpos.io.infile_handler import parse_infile



def get_index_by_group(labled_trajs, topology, group, stride=1):
    """ creates the unique ID index based on selected groups"""

    group_id = "g{}".format(group)

    index_lables = []
    for tag, trajpath in labled_trajs.items():
        if group_id in tag:
            trajobj = md.load(trajpath, top=topology, stride=stride)
            for idx in range(trajobj.n_frame):
                unique_indx = "{}_{}".format(tag, idx * stride)
                index_lables.append(unique_indx)

    return index_lables

def get_index_by_tag(labled_trajs, topology, tag, stride=1):

    trajobj = md.load(labled_trajs[tag], top=topology, stride=stride)
    index_labels = []
    for idx in range(trajobj.n_frames):
        unique_indx = "{}_{}".format(tag, idx*stride)
        index_labels.append(index_labels)



def get_index(labled_traj, topology, stride=1):
    """ Creats a unique index of all trajectories"""

    index_lables = []
    for tag, trajpath in labled_traj.items():
        trajobj = md.load(trajpath, top=topology, stride=stride)
        for idx in range(trajobj.n_frames):
            unique_indx = "{}_{}".format(tag, idx*stride)
            index_lables.append(unique_indx)

    return index_lables


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
    all_frame_index = get_index(labled_data, topfile, stride=stride)

    # ---------------------------------------------------------
    # Stage 1: Looking for native outlier
    # ---------------------------------------------------------
    for sel_group in groups:
        selected_group = []
        loaded_traj = iterload_by_group(labled_data, prmtop, sel_group)
        group_index = get_index_by_group(labled_data, topfile, sel_group)
        for tag in labled_data.keys():
            if tag.startswith(sel_group):
                selected_group.append(tag)

        df_frames = []
        for group_trajs, merged_trjs in loaded_traj:
            for traj in group_trajs:
                rmsd = calculate_rmsd(traj, merged_trjs, stride=stride) # generator of 1D arrays
                # creating a data frame for each trajobj in the group
                native_index = get_index_by_tag(labled_data, topfile, stride=stride)
                rmsd_df = pd.DataFrame(rmsd, index=native_index, columns=native_index)
                df_frames.append(rmsd_df)

        group_df = pd.concat(df_frames) # concatenates all df in the y direction

        # TODO: (stopped here) issue with the loader. does not load trajectories properly
        group_df.columns = all_frame_index
        group_df.index =  group_index


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

