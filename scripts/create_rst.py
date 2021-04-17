#!/home/exec/anaconda3/bin/python
import os 
import sys 
import shutil
import subprocess
import argparse
from textwrap import dedent
import mdtraj as md

__version__ = "0.1.1"

# formats user inputs for better input handling in the program
class FrameSelectionArgumentFormatter(argparse.Action):
    """ modifies input format to allow easy index selection """
    def __call__(self, parser, namespace, values, options_string=None):
        if "-" in " ".join(values):
            # frames within a range
            stringed_range = " ".join(values)
            start, end = tuple(stringed_range.split("-"))
            indicies = [i for i in range(int(start), int(end))]
            setattr(namespace, self.dest, indicies)
            # raise NotImplementedError("Range selection has not been tested yet")
        elif len(values) == 1:
            setattr(namespace, self.dest, int(values[0]))
        elif len(values) > 1:
            vals = [int(i) for i in values]
            setattr(namespace, self.dest, vals)
        else:
            raise ValueError("unrecognized index input format")


def cpptraj_executer(trajpath, toppath, frame, outname=None):
    """ writes an infile for cpptraj """

    with open("temp_cpptraj.in", "w") as cpptrajfile:
        if outname == None:
            outname = "restart_frame{}.rst".format(frame)
        else: 
            outname = "{}_frame{}.rst".format(outname, frame)
        cpptrajfile.write("parm {}\n".format(toppath))
        cpptrajfile.write("trajin {0} {1} {1}\n".format(trajpath, frame+1))
        cpptrajfile.write("trajout {} restart\n".format(outname))
        cpptrajfile.write("go\n")
        cpptrajfile.write("quit")

    cpptraj_cmd = "cpptraj -i temp_cpptraj.in".split()
    cpptraj_proc = subprocess.run(cpptraj_cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if cpptraj_proc.returncode != 0:
        raise subprocess.CalledProcessError("Cpptraj has captured and error, please run the code natively by typing 'cpptraj -i temp_cpptraj.in' on your terminal")

    print(".rst file created in: {}".format(os.path.realpath(outname)))
    os.remove("temp_cpptraj.in")

# checking mechanisms 
def check_input_params(trajpath, toppath, selected_frames):
    """ checks if the inputed trajectory exists """
    traj_check = os.path.exists(trajpath)
    prmtop_check = os.path.exists(toppath)
    if not traj_check:
        raise FileNotFoundError("Cannot not locate trajectory")
    if not prmtop_check:
        raise FileNotFoundError("Cannot not locate topology file")

    # checking if selected frame index is not out of bounds 
    topology = md.load_topology(toppath)
    trajObj_nframes = md.load(trajpath, top=topology).n_frames
    print("Trajectory contains {} frames".format(trajObj_nframes))
    if not isinstance(selected_frames, list):
        selected_frames = [selected_frames]
    index_check = all(frame_idx < trajObj_nframes for frame_idx in selected_frames)
    if index_check is False:
        out_of_bounds_indx = " ".join([str(out_idx) for out_idx in selected_frames if out_idx > trajObj_nframes])
        raise IndexError("Given frame index or indices {} excceds total number of frames of given trajectory: {} frames".format(out_of_bounds_indx, trajObj_nframes))

    
def help_message():
    print(dedent(""" 
    create_rst.py
    version: {}
    Creates restart files by utlizing cpptraj's functions.

    USECASE EXAMPLE:
    ---------------
    create_rst.py -x traj.nc -p top.prmtop -f 43 -o new_start_point           # single frame 
    create_rst.py -x traj.nc -p top.prmtop -f 50-100 -o new_start_point       # frames by range
    create_rst.py -x traj.nc -p top.prmtop -f 40 32 21 43 -o new_start_point  # multi independent frames
    
    ARGUMENTS
    ---------
    Required:
    -x, --trajs           Trajectory file 
    -p, --topology        Topology file (.prmtop)
    -f, --frameselection  Index selection by range or independent selection
    
    Optional:
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
    required = parser.add_argument_group("Required Arguments")
    optional = parser.add_argument_group("Optional Arguments")
    required.add_argument("-x", "--trajs", required=True, help="trajectoy paths")
    required.add_argument("-p", "--topology", type=str, required=True, help="Topology file. Example: File.prmtop")
    required.add_argument("-f", "--frameselection", nargs="+", type=str, required=True, action=FrameSelectionArgumentFormatter)
    optional.add_argument("-o", "--outname", type=str, required=False, default=None)
    args = parser.parse_args()

    # check mechanisms 
    # -- checking if cpptraj exists 
    cpptraj_check = shutil.which("cpptraj")
    if cpptraj_check is None:
        raise ValueError("Cannot find cpptraj executable")

    # -- checking if the input files exists (traj and prmtop files)
    check_input_params(args.input, args.topology, args.indexselection)

    if isinstance(args.indexselection, list):
        # only when a range is provided
        for frame_idx in args.indexselection:
            cpptraj_executer(args.input, args.topology, frame_idx, args.outname)
    else:
        # only for single value 
        cpptraj_executer(args.input, args.topology, args.indexselection, args.outname)

    print("Process Finished!")