# loading of file contents into memory from a file 
import mdtraj as md 
from itertools import combinations

from mdtraj.core import topology

def extract_contents(filename):
    contents = []
    with open(filename, "r") as file:
        for lines in file:
            contents.append(lines.strip("\n"))            
    
    return contents

def iterload_trajs(labled_trajs, topology, stride=1, method="by_two"):
    """ loads two trajectroies at a time 
    
    returns
    -------
    A tuple object that contains both the tag and the md.traj assign to it. 
    """
    merged_trajs = md.join(alltrajs)
    tags = list(labled_trajs.keys())

    if method == "by_two":
        comb = com(tags, 2)
        for i_tag, j_tag in comb:
            i_trajobj, j_trajobj = (md.load(labled_trajs[i_tag], top=topology, stride=stride),
                                    md.load(labled_trajs[j_tag], top=topology, stride=stride))
                
            yield [(i_tag, i_trajobj), (j_tag, j_trajobj)]
                
def iterload_by_group(labled_traj, topology, group_id):
    selelcted_group = []
    for tag in labled_data.keys():
        if tag.startswith(group_id):
           selelcted_group.append(tag)
    
    yield selected_group 