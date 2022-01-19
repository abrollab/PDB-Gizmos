# list of functions that handles the trajectories used in the program 
import os 

import mdtraj as md


def get_trajpath(traj_name):
    """ Takes in a list of trajectory names and creates aboslute paths

    inputs:
    ------
    traj_name {str}     inputed name of the trajectory 

    returns:
    --------
    absolute path of each trajectory name provided 
    """
    # check if input is a list format if not, create as one 
    if not isinstance(traj_name, list):
        traj_list = [traj_name]

    # iterate through each name 
    abs_trajpath = []
    for trajname in traj_list:
        path = os.path.abspath(traj_list)
        abs_trajpath.append(path)

    return abs_trajpath


def load_trajs(traj_path, topology, stride=1):
    """ With the given trajectory paths, it will create a trajectory object
    in order to ultize md.trajs functionality"""
    pass


