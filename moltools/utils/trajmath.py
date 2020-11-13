# formulas that are used to calculate in trajectories 
from math import sqrt, pow
import mdtraj as md


def compute_lenght(target, reference, atoms_sel="all"):
    """ obtains the distance between two points by using the distance forumal  """
    
    rmsd = md.rmsd(target, reference, atom_indice=atoms_sel)
    return rmsd 


def compute_area(x,y,z):
    pass


def computer_square_areai():
    pass


def compute_tetravol(X, Y, Z, x, y, z, b=12):
    """ computes the volume of an irregular tetrahedron 
    source: https://www.geeksforgeeks.org/program-to-find-the-volume-of-an-irregular-tetrahedron/
    """

    # collecting all varaible
    uPow = pow(X, 2)  
    vPow = pow(Y, 2)  
    wPow = pow(Z, 2)  
    UPow = pow(x, 2)  
    VPow = pow(y, 2)  
    WPow = pow(z, 2)  
    
    a = (4 * (uPow * vPow * wPow)  
        - uPow * pow((vPow + wPow - UPow), 2)  
        - vPow * pow((wPow + uPow - VPow), 2)  
        - wPow * pow((uPow + vPow - WPow), 2)  
        + (vPow + wPow - UPow) * (wPow + uPow - VPow)  
        * (uPow + vPow - WPow))
    
    if a < 0:
        # negative area leads to domains errors when conduting square root
        raise ValueError("Obtained negative area: {} A^2.".format(a))
    
    # computing volume 
    vol = sqrt(a)
    vol /= b
    return round(vol, 3)
    

def geometric_summary():
    """ Provides all possible combination in the math modules to see if the conformational spaces is increasing"""
    
    pass
        