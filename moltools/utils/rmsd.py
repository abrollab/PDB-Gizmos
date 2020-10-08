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


def rmsd_df(target_trajobj, ref_trajobj, sel_atoms=None, threads=4):
    """ returns a pandas DataFrame object containg the rmsd values per frame """
    os.environ["OPM_NUM_THREADS"] = "{}".format(threads)
    raw_rmsd = []
    for frame_num in range(ref_trajobj.n_frames):
        rmsd = np.round(md.rmsd(target_trajobj, ref_trajobj, frame=frame_num, atom_indices=sel_atoms) * 10, 3)
        raw_rmsd.append(rmsd.tolist())

    return pd.DataFrame(raw_rmsd)