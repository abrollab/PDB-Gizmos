#!/home/exec/anaconda3/bin/python
import os 
import sys 
import shutil
import subprocess
import argparse
from textwrap import dedent

# TODO: test multi index
# TODO: test range index
__version__ = "0.1.0"

# formats user inputs for better input handling in the program
class FrameSelectionArgumentFormatter(argparse.Action):
    """ modifies input format to allow easy index selection """
    def __call__(self, parser, namespace, values, options_string=None):
        if len(values) == 1:
            setattr(namespace, self.dest, values[0])
        elif "-" in values:
            # frames within a range
            start, end = tuple(values.split("-"))
            indicies = [i for i in range(start, end)]
            setattr(namespace, self.dest, indicies)
            raise NotImplementedError("Range selection has not been tested yet")
        else:
            raise ValueError("unrecognized index input format")


def cpptraj_executer(trajpath, toppath, frame, outname=None):
    """ writes an infile for cpptraj """

    with open("temp_cpptraj.in", "w") as cpptrajfile:
        if outname == None:
            outname = "restart_".format(frame)
        cpptrajfile.write("parm {}\n".format(toppath))
        cpptrajfile.write("trajin {0} {1} {1}\n".format(trajpath, frame+1))
        cpptrajfile.write("trajout {}_frame{}.rst restart\n".format(outname, frame))
        cpptrajfile.write("go\n")
        cpptrajfile.write("quit")

    cpptraj_cmd = "cpptraj -i temp_cpptraj.in".split()
    cpptraj_proc = subprocess.run(cpptraj_cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if cpptraj_proc.returncode != 0:
        raise subprocess.CalledProcessError("Cpptraj has captured and error, please run the code natively by typing 'cpptraj -i temp_cpptraj.in' on your terminal")

    print(".rst file created in: {}".format(os.path.realpath(outname)))
    os.remove("temp_cpptraj.in")

# checking mechanisms 
def check_files(trajpath, toppath):
    """ checks if the inputed trajectory exists """
    traj_check = os.path.exists(trajpath)
    prmtop_check = os.path.exists(toppath)
    if not traj_check:
        raise FileNotFoundError("Cannot not locate trajectory")
    if not prmtop_check:
        raise FileNotFoundError("Cannot not locate topology file")
    

def help_message():
    print(dedent(""" 
    create_rst.py
    version: {}
    Creates restart files by utlizing cpptraj's functions.

    USECASE EXAMPLE:
    ---------------
    create_rst.py -i traj.nc -t top.prmtop -x 43 -o new_start_point          # single frame 
    create_rst.py -i traj.nc -t top.prmtop -x 50-100 -o new_start_point      # frames by range
    create_rst.py -i traj.nc -t top.prmtop -x 40 32 21 43 -o new_start_point # multi independent frames
    
    ARGUMENTS
    ---------
    -i, --input           Trajectory file 
    -t, --topology        Topology file (.prmtop)
    -x, --indexselection  Index selection by range or independent selection
    -o, --output          name of the output rst files [Default: None]

    """).format(__version__))
    exit()


if __name__ == "__main__":

    if len(sys.argv) == 1:
        help_message()
    elif sys.argv[1] == "-h" or sys.argv[1].lower() == "--help":
        help_message()

    # CLI arguments 
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-i", "--input", required=True, help="trajectoy paths")
    parser.add_argument("-t", "--topology", type=str, required=True, help="Topology file. Example: File.prmtop")
    parser.add_argument("-x", "--indexselection", nargs="+", type=int, required=True, action=FrameSelectionArgumentFormatter)
    parser.add_argument("-o", "--outname", type=str, required=False, default=None)
    args = parser.parse_args()

    # check mechanisms 
    # -- checking if cpptraj exists 
    cpptraj_check = shutil.which("cpptraj")
    if cpptraj_check is None:
        raise ValueError("Cannot find cpptraj executable")

    # -- checking if the input files exists (traj and prmtop files)
    check_files(args.input, args.topology)

    if isinstance(args.indexselection, list):
        # only when a range is provided
        start, end = tuple(args.indexselection)
        for frame_idx in range(start, end):
            cpptraj_executer(args.input, args.topology, frame_idx, args.outname)
    else:
        # only for single value 
        cpptraj_executer(args.input, args.topology, args.indexselection, args.outname)

    print("Process Finished!")