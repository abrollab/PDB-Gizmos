from moltools.io.loader import extract_contents


class PdbEditor:
    
    def __init__(self, pdbfile):

        # checking if it is a list or a file 
        if isinstance(pdbfile, list):
            self.pdbfile = pdbfile
        else: 
            contents = extract_contents(pdbfile)
            self.pdbfile = contents 
            
        self.atom = None
        self.header = None
        self.footer = None
        
        
    def extract(self, file):
        """ When creating the pdbEditor object, this function is automatically 
        executed. The file gets converted into a list """
        
        raw_pdbfile = []
        with open(file, "r") as pdbfile:
            for lines in pdbfile:
                data = lines.split()
                raw_pdbfile.append(data)
                
        self.pdbfile = raw_pdbfile
        return self.pdbfile

        
    def add_elemtnCol(self):
        """ Adds single element letters in to the pdb file """
        pass
    
    
    def edit_chains(self, taget_id, new_id, range=None):
        """ edit the chain ID of the pdb file """
        pass
    
    
    def reset_resid(self):
        """ resets the numbering scheme of the resids starting at 1"""
        pass
    
    
    def display(self, range=None):
        """ displays what the current state of pdb file is """
        pass    