#!/home/exec/anaconda3/bin/python
import sys
import subprocess
import argparse
import shutil
from textwrap import dedent

__version__ = "0.1.0"

def count_frames(top_file, traj_paths):
    """Counts the number of frames 

    Arugments 
    ---------    
    top_file : str
        path pointing to topology file
    traj_paths : list
        list of trajectories paths

    Returns
    -------
    int
        total number of frames wtih given trajectories
    
    """

    traj_str = " ".join(traj_paths)
    cpptraj_cmd = ["cpptraj", "-p" , top_file, "-y", " ".join(traj_paths), "-tl"]
    # executing process
    proc = subprocess.run(cpptraj_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError("Cpptraj has captured and error, please run the code natively by typing {} on your terminal".format(" ".join(cpptraj_cmd)))
    n_frames = proc.stdout.decode("utf-8").split(":")[1].strip()
    return n_frames

def help_message():
    print(dedent("""
    total_frames.py
    version: {}
    Cpptraj python wrapper for counting total frames

    USECASE EXAMPLE:
    ---------------
    total_frames.py -x traj.nc -p top.prmtop 

    ARGUMENTS
    ---------
    Required:
    -x, --trajs           Trajectory file(s)
    -p, --topology        Topology file (.prmtop)
    """).format(__version__))
    exit()




if __name__ == "__main__":
       # checking if cpptraj is installed
    cpptraj_check = shutil.which("cpptraj")
    if not cpptraj_check:
        raise RuntimeError("Cannot find cpptraj xecutable")

    # checking help message
    if len(sys.argv) == 1:
        help_message()
    elif sys.argv[1] == "-h" or sys.argv[1].lower() == "--help":
        help_message()

    # cli args
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-p", "--topology", type=str, required=True)
    parser.add_argument("-x", "--trajectories", nargs="+", required=True)
    args = parser.parse_args()


    n_frames = count_frames(args.topology, args.trajectories)
    print(n_frames)