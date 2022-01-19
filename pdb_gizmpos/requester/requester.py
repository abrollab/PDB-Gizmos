import os
import requests

from pdb_gizmpos.editor.PdbEditor import PdbEditor


def opm_pdb(pdbid, store=False):
    """ Obtaining pdb structures from the OPM server

    arguemnts:
    ---------
    pdbid {str} :
    accession number that directes to a specific structureo

    stored {bool} :
    Stores the pdb ID in memory. If set to False, then the
    pdb file will be saved in current working directory.
    [Default: False]
    """

    API_URL = "https://opm-assets.storage.googleapis.com/pdb/{}.pdb".format(pdbid.lower())
    r = requests.get(API_URL)
    content = str(r.content).split("\\n")

    if not store:
        return content
    else:
        # file file will be stored in current working directory
        with open("{}.pdb".format(pdbid), "w") as dl_pdbfile:
            for lines in content:
                dl_pdbfile.write(lines + "\n")


def rcsb_pdb(pdbid, store=False):
    """ Obtaining pdb files from RCSB server"""
    API_URL = "https://files.rcsb.org/download/{}.pdb".format(pdbid.lower())
    r = requests.get(API_URL)
    rcsb_content = str(r.content).split("\\n")

    if not store:
        return rcsb_content
    else:
        with open("{}.pdb".format(pdbid), "w") as rcsb_file:
            for line in rcsb_file:
                rcsb_content.write(line + "\n")


