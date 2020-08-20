

class PdbEditor:
    
    def __init__(self, pdbfile):
        self.pdbfile = self.extract(pdbfile)
        
        
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

        
    def show(self):
        """ displays the data that is currently saved in the object """
        
        pdb_data = [line for line in self.pdbfile]
        return pdb_data
        