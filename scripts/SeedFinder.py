import os
import sys
import shutil
import argparse
import subprocess
from textwrap import dedent
from itertools import combinations
import textwrap

# 3rd party imports
import mdtraj as md
import pandas as pd
import numpy as np

#moltools imports
from pdb_gizmpos.utils.trajmath import compute_tetravol

def get_index(trajlist, topology, stride):
    """ returns an index of the trajectories"""

    indx = []
    for traj in trajlist:
        trajobj = md.load(traj, top=topology, stride=stride)
        for i in range(trajobj.n_frames):
            unique_idx = "{}_{}".format(traj, i)
            indx.append(unique_idx)

    return indx

def cpptraj_infile(f_name, frame, topfile, stride):
    """ creates a cpptraj infile

    returns:
        File path to the cpptraj.in file.
    """

    name = f_name.split(".")[0]
    new_name = "{}_{}".format(name, frame)
    infile_name = "cpptraj_{}_{}.in".format(name, frame)
    cpptraj_frame = (frame*stride)+1
    print("writting cpptraj infile for seed traj: {0}_frame: {1} ----> cpptraj_{0}_{1}.in".format(name, frame))
    with open(infile_name, "w") as cppfile:
        cppfile.write("parm {}\n".format(topfile))
        cppfile.write("trajin {0}.nc {1} {1}\n".format(name, cpptraj_frame))
        cppfile.write("trajout {}.pdb\n".format(new_name))
        cppfile.write("trajout {}.rst restart\n".format(new_name))
        cppfile.write("run")

    return os.path.abspath(infile_name)

def loader(trajlist, topology, stride=1, atom_sel="protein"):
    """ Load the preprocessed trajectoy onto memeory and returns a md.Traj
    and md.Topology object"""

    if not isinstance(trajlist, list):
        trajlist = list(trajlist)

    atom_idx = select_atoms(topology, atom_sel)

    mereged_obj = md.load(trajlist, top=topology, stride=stride).atom_slice(atom_idx)
    return mereged_obj


def select_atoms(topobj, atomtypes):
    atom_idx = md.load_topology(topobj).select(atomtypes)
    return atom_idx


def calculate_rmsd(trajobj, atoms_idx=None, cores=4):
    """ Uses the mdTraj trajectory and topology objects to calculate rmsd
    returns 1-D array of rmsd values
    """

    # setting up multiprocessing
    os.environ["OMP_NUM_THREADS"] = "{}".format(cores)
    rmsd = [np.round(np.average(md.rmsd(trajobj, trajobj, frame=i, atom_indices=atoms_idx))*10, 3) for i in range(trajobj.n_frames)]
    return rmsd


def find_seeds(rmsd_df, n_seeds):
    """ Uses the dataframe created from calcuate_rmsd and selects top seeds.
    n_seeds represents the amount of seeds extracting from this

    returns a tuple (trajname, framenum)
    """
    highest_rmsd_df = rmsd_df.sort_values(ascending=False).head(n_seeds)
    highest_rmsd = list(zip(highest_rmsd_df, highest_rmsd_df.index))

    print("These are the selected seeds... {}".format(highest_rmsd))
    return highest_rmsd

def get_distance(seeds, topobj, sel_atoms):
    """ Returns a dictionary of distances of selected seeds"""
    labled_traj = {}

    for _, seed_name in seeds:
        lables = tuple(seed_name.split("_"))
        trajname = "_".join(lables[:-1])
        frame = int(lables[-1])
        seed = md.load(trajname, top=topobj)[frame].atom_slice(sel_atoms)
        labled_traj["{}_{}".format(trajname, frame)] = seed
        print(seed)

    dist_lables = {}
    lables = list(labled_traj.keys())
    comb_pairs= combinations(lables, 2)
    for seedx, seedy in comb_pairs:
        seedx_name, seedx_frame = tuple(seedx.rsplit("_", 1))
        seedy_name, seedy_frame = tuple(seedy.rsplit("_", 1))
        dist = np.round(md.rmsd(labled_traj[seedx], labled_traj[seedy])*10, 3)

        print("distance between {} frame:{} and {} frame:{} is {}".format(seedx_name, seedx_frame, seedy_name, seedy_frame, dist))
        dist_lables["{} -- {}".format(seedx, seedy)] = round(float(dist),3)


    return dist_lables

def exec_cpptraj(infile):
    """ calls the cpptraj program with the created script from SeedFinder"""
    cmd = "cpptraj -i {}".format(infile).split()
    subprocess.run(cmd, shell=False)


def help_message():
    print(textwrap.dedent("""
    -i, --input         Traejctories files

    -t, --topology      Topology prmtop file

    -s, --stride        Loading of every nth frame (default = 1)

    -n, --numberseeds   Number of seeds (locked at 4)

    -a, --atomtype      Range of atoms taken account for calculations
                        [default = "protein"]
                        [Options: "backbone","CA","sidechain", "protein",
                        "protein and sidechain", "protein and backbone"]
                        """))


if __name__ == "__main__":

    # Help message

    if len(sys.argv) == 1:
        help_message()

    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        help_message()

    # CLI Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', nargs='+', type=str, required=True)
    parser.add_argument('-t', '--topology', type=str, required=True)
    parser.add_argument('-s', '--stride', type=int, required=False, default=1)
    parser.add_argument('-n', '--numberseeds', type=int, required=False, default=4)
    parser.add_argument('-a', '--atomtype', type=str, default="protein", choices=["backbone","CA","sidechain", "protein", "protein and sidechain", "protein and backbone"])
    args = parser.parse_args()

    # executing program
    prmtop = md.load_prmtop(args.topology)
    loaded_data = loader(args.input, args.topology, stride=args.stride) # loaded traj object
    indx = get_index(args.input, prmtop, stride=args.stride)

    # atom selection if it is not flagged default is None --> all atoms (mdtraj docs)
    atoms = select_atoms(args.topology, args.atomtype)

    #preprocessing the trajectories
    if shutil.which("cpptraj") is None:
       raise FileNotFoundError("The 'cpptraj' cannot be found")

    print("Selected atom ids:\n", atoms)
    rmsd = calculate_rmsd(loaded_data, atoms)
    # rmsd_df = pd.DataFrame(rmsd.aver, columns=indx, index=indx)
    rmsd_series = pd.Series(rmsd, index=indx)
    selected_seeds = find_seeds(rmsd_series, args.numberseeds)

    # writting cpptraj infiles
    for rmsd, seed_name in selected_seeds:
        lables = tuple(seed_name.split("_"))
        trajname = "_".join(lables[:-1])
        frame = int(lables[-1])
        infile = cpptraj_infile(trajname, frame, args.topology, args.stride)
        print("executing cpptraj with {}".format(infile))
        #exec_cpptraj(infile)


    labled_dists = get_distance(selected_seeds, prmtop, atoms)
    dist_values = list(labled_dists.values())
    dist_values = dist_values[:4] + [dist_values[-1]] + [dist_values[-2]] # swapping last two
    # print("DEBUGG: edge distances are: {}\n".format(dist_values))

    sampled_region_calc = compute_tetravol(*dist_values)
    print("samples region is {} A^3".format(sampled_region_calc))