import mdtraj as md
import numpy as np


def traj_rmsd(traj, topology, stride=1, sel_atoms=None):
    """ A genorator that returns rmsd values for each frame """

    if not isinstance(traj, md.core.trajectory):
        prmtop = md.load_topology(topology)
        traj = md.load(traj, top=prmtop, stride=stride)

    for frame_num in range(traj.n_frames):
        raw_rmsd = np.round(md.rmsd(traj, traj, frame=frame_num, atom_indices=sel_atoms) * 10, 3)
        yield raw_rmsd
    
        
