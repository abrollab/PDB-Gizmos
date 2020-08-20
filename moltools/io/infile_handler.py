import os 
import json

# NOTE: These functions provided below refers the handling of how
# the input file is created or used for programs 
# TODO: Think of a standard methods for the infile 


def parse_infile(infile):
    """ Parses the input file used for scripts 
    infile {str}:    Path to the generated input file

    returns {dict}: 
    A hashed tabled where each trajectory is mapped to a 
    unique tag.
    """

    if not os.path.exists(infile):
        raise FileExistsError("The required input file does not exists")
    else:
        with open(infile, "r") as f: 
            for param in f:
                print(param)
    pass


def write_infile(traj_paths):
    """ Writes the infile for scripts in a JSON format

    ## sample format 
    {
        "group": "g0"
        "traj": [
            "t0" : " traj1.nc",
            "t1" :  " traj2.nc"
        ]
    """
    pass







