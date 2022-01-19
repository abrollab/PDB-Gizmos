import os 
import mdtraj as md
from numpy.core.fromnumeric import trace
import pandas as pd 
import numpy as np

def calculate_rmsd(target_trajobj, ref_trajobj, stride=1, threads=4):
    """ a generator that returns a 1D rmsd array """
    os.environ["OPM_NUM_THREADS"] = "{}".format(threads)
    for frame_num in range(target_trajobj.n_frames):
        rmsd = md.rmsd(target_trajobj, ref_trajobj, frame=frame_num)
        yield rmsd 

def rmsd_from_crystal(trajobj,  crystal, frame=1, atom_ids=None):
    """rmsd_from_crystal

    Caclulates the rmsd between selected frames of a trajectory 
    and a known crystal structure

    Parameters
    ----------
    trajobj : MdTraj obj 
        MdTrajectory object container that holds the trajectory 
    
    crystal : MdTraj obj
        Md Trajector object that contains the pdb informations.
        Hint: use md.load("path/to/pdb") in order to conver
        your pdb file into and Md Trajobject 
    
    frame : int
        Selected frame number from the corresponding "traj" input
        [default: frame=1]
    
    atom_ids : list[int] or np.array[int]
        a list or array of postive integers that will be focused 
        when conducting rmsd calculations
    
    returns
    -------
    float 
        rmsd value    
    """
    
    # load the crystal structure into a pdb obj
    if not isinstance(trajobj, md.Trajectory) and not isinstance(crystal, md.Trajectory):
        raise ValueError("Inncorrect format provided. trajectory and pdbfiles must be in md.Trajectory format you have prodvided traj:{}, pdb:{}".format(type(trajobj), type(crystal)))
    
    rmsd = md.rmsd(crystal, trajobj, frame=frame, atom_indices=atom_ids)
    return rmsd 


def rmsd_df(target_trajobj, ref_trajobj, sel_atoms=None, threads=4):
    """ returns a pandas DataFrame object containg the rmsd values per frame """
    os.environ["OPM_NUM_THREADS"] = "{}".format(threads)
    raw_rmsd = []
    for frame_num in range(ref_trajobj.n_frames):
        rmsd = np.round(md.rmsd(target_trajobj, ref_trajobj, frame=frame_num, atom_indices=sel_atoms) * 10, 3)
        raw_rmsd.append(rmsd.tolist())

    return pd.DataFrame(raw_rmsd)