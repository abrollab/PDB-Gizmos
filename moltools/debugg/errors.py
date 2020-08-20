################################################################################
# error.py 
# Class that allows to to write user defined errors to better understand the 
# program. 

# Replaced pythons standard error and it converted into user defined errors. 
################################################################################


class PdbRequestFailed(ValueError):
    """ Error is used when a request is sent and fails to respond"""

        
class InvalidPDBFile(ValueError):
    """ raised when formatting of the pdbFile is not met """

    
class MissingDependency(Exception):
    """ Instances where depdenencies are not me """
