#!/home/exec/anaconda3/bin/python
import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime
from textwrap import dedent

# version
__version__ = '0.1.1'


class CheckResRangeFormat(argparse.Action):
    """ checking the input format for the res range"""
    def __call__(self, parser, namespace, values, options_string=None):
        range_check = values.split()
        if len(range_check) != 3 and len(range_check) != 1:
            raise ValueError("Incorrect format or invalid argument values provided: Example argumet input: '-r 100-300'")

        selected_range = "".join(values.split())
        setattr(namespace, self.dest, selected_range)

def cpptraj_executer(trajpaths, top_file, resrange=None, outname=None):
    """ writes input file and executes cpptraj """
    with open("temp_cpptraj.in", "w") as cpptraj_infile:
        cpptraj_infile.write("parm {}\n".format(top_file))

        for traj_path in trajpaths:
            cpptraj_infile.write("trajin {}\n".format(traj_path))

        # selecting moelcule if not using cpptraj default selection
        if resrange is None:
            print("WARNING: No resiude range was not provided. Applying Cpptraj's default paramters")
            cpptraj_infile.write("autoimage\n") # cpptraj default select unspecified molecule
        else:
            print("Applying focusing to resiude range {} for auto imaging".format(resrange))
            cpptraj_infile.write("autoimage :{}\n".format(resrange))

        # output
        cpptraj_infile.write("trajout {}.nc\n".format(outname))
        cpptraj_infile.write("go")

    cpptraj_cmd = "cpptraj -i temp_cpptraj.in".split()
    cpptraj_proc = subprocess.run(cpptraj_cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if cpptraj_proc.returncode != 0:
        raise subprocess.CalledProcessError("Cpptraj has captured and error, please run the code natively by typing 'cpptraj -i temp_cpptraj.in' on your terminal")

    print("Autoimaged trajectory created in: {}.nc".format(os.path.realpath(outname)))
    #os.remove("temp_cpptraj.in")


def help_message():
    print(dedent("""
    autoimage.py
    version: {}
    Cpptraj python wrapper for autoimaging trajectories.

    USECASE EXAMPLE:
    ---------------
    autoimage.py -x traj.nc -p top.prmtop -r 50-100 -o new_start_point

    ARGUMENTS
    ---------
    Required:
    -x, --trajs           Trajectory file(s)
    -p, --topology        Topology file (.prmtop)

    Optional:
    -r, --resrange        Index selection by range [Default: None]. If None,
                          it will utlize Cpptraj default parameters. If range
                          is provided, autoimaging will focus on that range.
    -o, --output          name of the output rst files [Default: None]

    """).format(__version__))
    exit()


if __name__ == "__main__":

    # checking if cpptraj is installed
    cpptraj_check = shutil.which("cpptraj")
    if not cpptraj_check:
        raise RuntimeError("Cannot find cpptraj xecutable")

    # checking help message
    if len(sys.argv) == 1 or len(sys.argv) == 2:
        help_message()
    elif sys.argv[1] == "-h" or sys.argv[1].lower() == "--help":
        help_message()
    elif sys.argv[2] == "-h" or sys.argv[2].lower() == "--help":
        help_message()

    # CLI Arguments
    parser = argparse.ArgumentParser(add_help=False)
    required = parser.add_argument_group("Required Arguments")
    optional = parser.add_argument_group("Optional Arguments")
    required.add_argument("-x", "--trajs", nargs="+", required=True)
    required.add_argument("-p", "--topology", type=str, required=True)
    required.add_argument("-o", "--output", type=str, required=True, default=None)
    optional.add_argument("-r", "--resrange", type=str, action=CheckResRangeFormat, required=False, default=None)
    args = parser.parse_args()

    # main code
    # -- creating cpptraj inputfile and executing cpptraj
    cpptraj_executer(args.trajs, args.topology, resrange=args.resrange, outname=args.output)
