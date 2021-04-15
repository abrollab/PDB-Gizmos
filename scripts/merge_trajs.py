#!/home/exec/anaconda3/bin/python
import os
import sys
import argparse
from datetime import datetime
from textwrap import dedent

import mdtraj as md

# version
__version__ = "0.1.0"


def traj_merger(traj_paths, top_path, stride=1):
    """ Takes the list of trajectory file paths and merges them into one
    trajectory object
    returns:
    -------
        - md.Trajectory Object
    """
    os.environ["OMP_NUM_THREADS"] = "4"
    top = md.load_topology(top_path)
    print("loading trajectories with a stride of {}".format(stride))
    list_of_trajobjs = []
    for traj_path in traj_paths:
        trajobj = md.load(traj_path, top=top, stride=stride)
        print("Loaded: {} with {} frames".format(traj_path, trajobj.n_frames))
        list_of_trajobjs.append(trajobj)

    print("Merging all trajectories")
    merged_traj = md.join(list_of_trajobjs)
    return merged_traj


def save_traj(trajobj, outname=None, traj_format="nc"):
    """ Saves trajectory to disk """

    # using default naming if output name is not provided
    if outname is None:
        outname = "merged_trajectory-{}".format(datetime.now().strftime("%m%d%y-%H%M%S"))

    supported_formats = ["xtc", "nc"]

    print("Saving as '.{}' format".format(traj_format))
    if traj_format == "nc":
        trajobj.save_netcdf("{}.nc".format(outname))
    elif traj_format == "xtc":
        trajobj.save_netcdf("{}.xtc".format(outname))
    else:
        raise ValueError("Unsupported format given. Supported formats are: ".format(supported_formats))

    file_name = "{}.{}".format(outname, traj_format)
    print("Merged trajctory saved in: {}".format(os.path.realpath(file_name)))


def help_message():
    """ Display program help message """
    print(dedent("""
    merge_trajs.py
    version: {}
    Script that takes in multiple trajectories and merges them into one

    USECASE EXAMPLE:
    ---------------
    merge_trajs.py -i traj1.nc traj2.nc -t top.prmtop -s 10 -f nc -o merged_5nx2_100ns
    merge_trajs.py -i traj1.nc traj2.nc -t top.prmtop -s 10 -f xtc -o merged_5nx2_100ns
    merge_trajs.py -i traj1.nc traj2.nc -t top.prmtop -s 10 -f nc -o merged_5nx2_100ns --removetrajs

    ARGUMENTS
    ---------
    Required:
    -i, --input    Trajectory file path
    -t, --topology Topology file (.prmtop)

    Optional:
    -s, --stride   loading trajectories with given stride [Default: 1]
    -o, --output   Name of the output trajectory file [Default: None]
    -f, --format   Output trajectory format [Default: "nc"] [Options: "nc", "xtc"]

    FLAGS (optional)
    -----
    --removetrajs  Deletes provided trajectories from disk after being merged.
                   [Default: False]
    """).format(__version__))
    exit()

if __name__ == "__main__":

    # Help message
    if len(sys.argv) == 1:
        help_message()
    elif sys.argv[1] == "-h" or sys.argv[1].lower() == "--help":
        help_message()

    # CLI arguments
    parser = argparse.ArgumentParser(add_help=False)
    required = parser.add_argument_group("Required Arguments")
    optional = parser.add_argument_group("Optional Arguments")
    required.add_argument("-i", "--input", nargs="+", required=True)
    required.add_argument("-t", "--topology", type=str, required=True)
    optional.add_argument("-s", "--stride", type=int, required=False, default=1)
    optional.add_argument("-o", "--outname", type=str, required=False, default=None)
    optional.add_argument("-f", "--format", type=str, required=False, default="nc")
    optional.add_argument("--removetrajs", action="store_true", required=False, default=False)
    args = parser.parse_args()

    # main code
    # -- load trajectories and merge them
    merged_trajobj = traj_merger(args.input, args.topology, stride=args.stride)

    # -- saving merged trajectory into disk
    save_traj(merged_trajobj, outname=args.outname, traj_format=args.format)

    # -- Checking if `removetrajs` flag is true
    if args.removetrajs:
        print("WARNING: Deleting provided trajectories from disk requires user response")

        # User response section
        attempts = 0
        while True:
            user_response = input("Do you want to delete {} from disk? (y/n): ".format(" ".join(args.input)))

            # attempt checker
            if attempts == 3:
                print("Skipping process. Too many attempts")
                break

            # response actions
            if user_response.lower() == "y":
                for traj_path in args.input:
                    print("Deleting: {}".format(traj_path))
                    os.remove(traj_path)
                break
            elif user_response.lower() == "n":
                print("Skipping step")
                break
            else:
                print("{} is an invalid response. Please try again".format(user_response))
                attempts += 1

    print("Process complete!")