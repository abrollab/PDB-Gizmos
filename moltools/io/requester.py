import os 
import requests 


from moltools.pdbeditor.PdbEditor import PdbEditor

def opm_pdb(pdbid, store=False):
    """ Obtaining pdb structures from the OPM server 

    arguemnts:
    ---------
    pdbid {str} :     
    accession number that directes to a specific structureo

    clean {bool} :
    Removes the dummy atoms [Default: False]

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
    pass


    