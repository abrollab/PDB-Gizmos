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


def compute_tetravol(a1, a2, a3, a4, a5, a6):
    """ computes the volume of an irregular tetrahedron
    """

    # Tetrahedron using formula
    a12 = pow(a1, 2)
    a22 = pow(a2, 2)
    a32 = pow(a3, 2)
    a42 = pow(a4, 2)
    a52 = pow(a5, 2)
    a62 = pow(a6, 2)

    # segmenting the tetrahedron volume formula
    f1 = a12*a52*(a22+a32+a42+a62-a12-a52)
    f2 = a22*a62*(a12+a32+a42+a52-a22-a62)
    f3 = a32*a42*(a12+a22+a52+a62-a32-a42)
    f4 = -(a12*a22*a42)-(a22*a32*a52)-(a12*a32*a62)-(a42*a52*a62)

    a = (1/144.0)*(f1+f2+f3+f4)
    if a < 0:
        raise ValueError("Obtained a negative area {}".format(a))

    vol = round(sqrt(a),3)
    print("Sampled volume is: {}".format(vol))
    return vol


def geometric_summary():
    """ Provides all possible combination in the math modules to see if the conformational spaces is increasing"""
    pass
