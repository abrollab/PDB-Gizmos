# NOTE: list of functions that connects to the rcsb database 
import os 
import requests 


def rcsb_pdb(pdbid, store=False):
    """ Obtaining pdb files from RCSB server"""
    API_URL = "https://files.rcsb.org/download/{}.pdb".format(pdbid.lower())
    r = requests.get(API_URL)
    contents = r.text

    if not store:
        rcsb_content = str(contents).split("\n")
        return rcsb_content
    else:
        file_name = "{}.pdb".format(pdbid.lower())
        with open(file_name, "w") as file:
            file.write(contents)

        pdb_path = os.path.abspath("{}.pdb".format(pdbid.lower()))

        return pdb_path
