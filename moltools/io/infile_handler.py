import os 
import json

# NOTE: These functions provided below refers the handling of how
# the input file is created or used for programs 
# TODO: new standard will be a JSON file 


def parse_infile(infile):
    """ Parses the input file used for scripts 
    infile {str}:    Path to the generated input file

    returns {dict}: 
    A hashed tabled where each trajectory is mapped to a 
    unique tag.
    """

    if not os.path.exists(infile):
        raise FileExistsError("The required input file does not exists")

    # saving all the labeled data
    with open(infile, 'r') as f_input:
        contents = []
        for line in f_input:
            raw_data = line.strip()
            contents.append(raw_data)

    traj_data = [contents[i:i + 2] for i in range(0, len(contents), 2)]

    # converting sub list into a dictionary
    hashed_trajs = {}
    for data in traj_data:
        subgroup_name = data[0]
        traj_list = data[1:]
        for trajs in traj_list:
            ntrajs = trajs.split(',')
            hashed_trajs[subgroup_name] = ntrajs

    # adding unique tags 
    labled_trajs = {}
    for group, traj_list in hashed_trajs.items():
        for indx, trajname in enumerate(traj_list):
            labled_trajs["{}t{}".format(group, indx)] = os.path.abspath(trajname)      
            
    return labled_trajs

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







