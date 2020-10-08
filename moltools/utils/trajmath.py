# formulas that are used to calculate in trajectories 
from math import sqrt, pow

def compute_lenght(target, reference, atoms="all"):
    """ obtains the distance between two points by using the distance forumal  """

    atom_selection = 

    pass

def compute_area(x,y,z):
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
        - yPow * pow((xPow + zPow - XPow), 2)  
        - yPow * pow((zPow + xPow - YPow), 2)  
        - zPow * pow((yPow + xPow - ZPow), 2)  
        + (yPow + zPow - XPow) * (zPow + xPow - YPow)  
        * (yPow + xPow - ZPow))
     
    vol = round((sqrt(a))/b, 3)
    
    return vol  

def geometric_summary():
    """ Provides all possible combination in the math modules to see if the conformational spaces is increasing"""
    
    pass