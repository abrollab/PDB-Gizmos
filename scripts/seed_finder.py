import os 
import shutil
import argparse
from textwrap import dedent
from collections import defaultdict
import textwrap

import mdtraj as md
import pandas as pd 
import numpy as np

def input_parser(input_file):
    """ Parses the input file and lables the trajectoy """
    # saving all the laveled data
    with open(input_file, 'r') as f_input:
        raw_input = []
        for line in f_input:
            raw_data = line.strip()
            raw_input.append(raw_data)

    traj_data = [raw_input[i:i + 2] for i in range(0, len(raw_input), 2)]

    # converting sub list into a dictionary
    # labled_data = {}
    labled_data = defaultdict(list) 
    for data in traj_data:
        subgroup_name = data[0]
        traj_list = data[1:]
        for trajs in traj_list:
            ntrajs = trajs.split(',')
            for traj_name in ntrajs:
                path = os.path.abspath(traj_name)
                labled_data[subgroup_name].append(path)


    return labled_data

def preproccess_trajs(labled_data, topology):
    """ Uses the labled trajectory path and preprocesses it with cpptraj"""
    # NOTE: this can be an issue when dealing with multiple molecule structures 
    res_count = md.load_topology(topology).n_residues
    os.mkdir("preprocess_trajs") 
    preproc_tag = "prep_"
    
    labled_preproc = {}
    for subgroup, traj_list in labled_data.items():
        count_traj = 0
        for trajname in traj_list:
            preproc_trajname = "{}_{}".format(preproc_tag, trajname)
            with open("cpptraj.in", "w") as cppfile:
                cppfile.write("parm {}".format(topology))
                cppfile.write("trajin {}".format(trajname))
                cppfile.write("autoimage anchor :1-{}".format(res_count))
                cppfile.write("strip !:1-{} outprefix strip".format(res_count))
                cppfile.write("trajout {}".format(preproc_trajname))
                cppfile.write("run")
            
            # file handling commmands
            preproc_path = shutil.move("{}".format(preproc_trajname), "preprocess_trajs") 
            preproc_abspath = os.path.abspath(preproc_path)
            
            # save labled preprocessed trajectory path and unique tags 
            labled_preproc["{}t{}".format(subgroup, count_traj)] = preproc_abspath
    
    return labled_preproc


def loader(labled_preproc, topology, stride=1):
    """ Load the preprocessed trajectoy onto memeory and returns a md.Traj
    and md.Topology object""" 

    prmtop = md.load_topology(topology)
    labled_trajobj = {}
    for group, traj_list in labled_preproc.items():
        traj_count = 0
        for traj in traj_list:
            tag = "{}t{}".format(group, traj_count)
            traj_obj = md.load(traj, top=prmtop, stride=stride) 
            labled_trajobj[tag] = traj_obj
            traj_count += 1
        
    return labled_trajobj

def select_atoms(topology, atomtypes):
    atom_idx = md.load_topology(topology).select(atomtypes)
    return atom_idx 

def calculate_rmsd(labled_trajob, atoms_idx=None):
    """ Uses the mdTraj trajectory and topology objects to calculate rmsd """
    
    # merging trajectories 
    trajobj_list = list(labled_trajob.values())

    if len(trajobj_list) > 1:
        trajobj = md.join(trajobj_list) 
    else:
        trajobj = trajobj_list[0]

    # calculating rmsd 
    avg_rmsd_list = []
    for idx in range(trajobj.n_frames):
        # TODO: add atom indices later 
        rmsd = np.round(md.rmsd(trajobj, trajobj, frame=idx, atom_indices=atoms_idx )* 10, 3)
        avg_rmsd = np.average(rmsd)
        avg_rmsd_list.append(avg_rmsd)
    
    #lableing the data 
    col_row_indx = []
    for tag, trajobj in labled_trajob.items():
        traj_indx = 0
        for frame_idx in range(trajobj.n_frames):
            unique_tag = "{}_{}".format(tag, frame_idx)
            col_row_indx.append(unique_tag)
            traj_indx += 1
        
    # creating series of 
    avg_rmsd_series = pd.Series(avg_rmsd_list, index=col_row_indx)
    
    return avg_rmsd_series


def find_seeds(rmsd_df, n_seeds=3):
    """ Uses the dataframe created from calcuate_rmsd and selects top seeds. 
    n_seeds represents the amount of seeds extracting from this 
    """
    highest_rmsd = rmsd_df.sort_values(ascending=False).head(n_seeds)
    return highest_rmsd


def help_message():
    print(textwrap.dedent("""
    no help message has been added yet
                           """))


if __name__ == "__main__":
    
    # Help message 
    # CLI Arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-t', '--topology', type=str, required=True)
    parser.add_argument('-s', '--stride', type=int, required=False, default=1)
    parser.add_argument('-a', '--atomtype', type=str, default=None)
    args = parser.parse_args()    

    # executing program
    labled_data = input_parser(args.input)
    loaded_data = loader(labled_data, args.topology, stride=args.stride)

    if args.atomtype is not None: 
        atoms = select_atoms(args.topology, args.atomtype)
    
    rmsd = calculate_rmsd(loaded_data, atoms)
    selected_seeds = find_seeds(rmsd)