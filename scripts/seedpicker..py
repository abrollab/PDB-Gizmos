# This is a the final version
import os
import sys
import argparse
import textwrap


# third party moduleπ
import numpy as np
from numpy.core.defchararray import index
import pandas as pd
import mdtraj as md

# pdbTools modules
from moltools.debugg.logger import Logger
from moltools.io.loader import iterload_by_group
from moltools.utils.rmsd import calculate_rmsd
from moltools.io.custom_args import ParseSelection
from moltools.io.infile_handler import parse_infile

def get_index_by_group(labled_trajs, topology, group, stride=1):
    """ Returns a np.array containg the index of each frame within a group """
    group_id = "g{}".format(group)

    index_arr = np.array([])
    for tag, trajpath in labled_trajs.items():
        if group_id in tag:
            trajobj = md.load(trajpath, top=topology, stride=stride)
            for idx in range(trajobj.n_frame):
                unique_indx = "{}_{}".format(tag, idx * stride)
                index_arr = np.append(index_arr, unique_indx)

    return group_id


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


    #-----------
    # setting up the files
    #-----------

    logger = Logger("seedpicker.log")
    prmtop = md.load_prmtop(args.topology)

    # NOTE: this might change when the new input files is releasd
    labled_data = parse_infile(args.input)
    groups = [tag.split('t')[0] for tag in labled_data.keys()]

    # -----------
    # SeedPicker starts here
    # -----------

    for selected_group in groups:
        selected_groups = []
        load_traj = iterload_by_group(labled_data, prmtop, selected_group)
        group_index = get_index_by_group(labled_data, prmtop, selected_groups)