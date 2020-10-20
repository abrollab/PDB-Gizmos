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
    xPow = pow(x, 2)  
    yPow = pow(y, 2)  
    zPow = pow(z, 2)  
    XPow = pow(X, 2)  
    YPow = pow(Y, 2)  
    ZPow = pow(Z, 2) 

    # computing the area 
    a = (4 * (xPow * yPow * zPow)  
        - xPow * pow((yPow + zPow - XPow), 2)  
        - yPow * pow((zPow + xPow - YPow), 2)  
        - zPow * pow((xPow + yPow - ZPow), 2)  
        + (yPow + zPow - XPow) * (zPow + xPow - YPow)  
        * (xPow + yPow - ZPow))
    
    # computing volume 
    vol = sqrt(a)
    vol /= b
    return round(vol, 3)
    

def geometric_summary():
    """ Provides all possible combination in the math modules to see if the conformational spaces is increasing"""
    
    pass