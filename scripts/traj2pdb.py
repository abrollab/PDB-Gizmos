import os
import sys
import mdtraj as md
import argparse
import textwrap

__version__ = '1.0.0'

# NOTE: todo list 
# TODO: implement logger

def loader(traj_file, top_file, stride):
    """loads the trajectory onto memory"""
    # setting up trajectory opbkect
    print('MESSAGE: Loading trajectory with a stride of {}'. format(stride))
    prmtop = md.load_prmtop(top_file)
    traj = md.load(traj_file, top=prmtop, stride=stride)
    print('MESSAGE: Total of {} frames loaded'. format(traj.n_frames))
    return traj


def slicetraj(traj, outname, slice_indxs, fmt='nc'):

    if len(slice_indxs) >= 2 and len(slice_indxs) % 2 == 0:
        slice_ranges = list(zip(*[iter(slice_indxs)] * 2))
        if fmt == 'nc':
            for f_range in slice_ranges:
                traj_writer(traj, outname, f_range)
        if fmt == 'pdb':
            for f_range in slice_ranges:
                traj2pdb(traj, outname, indx_list=f_range)
    else:
        raise ValueError('The provided slice range(s) is incorrectly formated. Keep in mind that slice_range require and beginning and end')


def create_rst(traj: md.Trajectory, outname: str, idx: int):
    if idx is None:
        last_frame = traj.n_frames
        traj[last_frame].save_amberst('{}_frame{}.rst'.format(outname,
                                                              last_frame))

    elif isinstance(idx, list):
        for i in idx:
            traj[i].save_amberrst7('{}_frame{}.rst'.format(outname, i))

# ------------------
# writer functions
# ------------------
def traj2pdb(traj_obj, outname, indx_list=None, all_frames=False):
    """ takes in trajectory and forms it into pdb snapshots"""

    # creating a directory to store all frames
    cwd = os.getcwd()
    if not os.path.exists('./{}_pdbFrames'.format(outname)):
        os.mkdir('{}_pdbFrames'.format(outname))
    else:
        raise FileExistsError("the direcotry {}_pdbFrames already exists. Please use a different name".format(outname))

    os.chdir('{}_pdbFrames'.format(outname))
    if indx_list is None:

        # iterate through trajectory and save nth frame
        print('No index provided')
        print(traj_obj.n_frames)
        for indx in range(traj_obj.n_frames):
            traj_obj[indx].save_pdb('{}_frame{}.pdb'.format(outname, indx))

        os.chdir(cwd)
        exit()

    elif indx_list is not None:
        if all_frames is True:
            if len(indx_list) != 2:
                raise ValueError('{} is not a range. Please select to numbers to indicate a range'.format(indx_list))
            start_frame = indx_list[0]
            end_frame = indx_list[1] + 1
            for idx in range(start_frame, end_frame):
                traj_obj[idx].save_pdb('{}_frame{}.pdb'.format(outname, idx))
            exit()
        else:
            for frame_indx in indx_list:
                traj_obj[frame_indx].save_pdb('{}_frame_{}.pdb'.format(outname, frame_indx))
    else:
        raise RuntimeError('An error has occured')


def traj_writer(traj, out_name, f_range=None):
    """Takes in a trajectory and returns a new trajectory with the given paramters"""

    if f_range is not None:
        starting_frame = f_range[0]
        ending_frame = f_range[1]
        traj[starting_frame:ending_frame+1].save_netcdf('{}_frame{}_to_{}.nc'.format(out_name, starting_frame, ending_frame+1))
    else:
        traj.save_netcdf('{}.nc'.format(out_name))


def help_message():
    print(textwrap.dedent("""
    Is a light weight program that provides simple functions to attend basic
    and most common issues in regards of handling simulation files

    [use case]
    traj2pdb.py -i trajfile.nc -t topology.prmtop -o outname --type-of-mode

    traj2pdbi -i A2A_sim.nc -t A2A_top.prmtop -o A2A_rst --create-rst

    [Arguments]

    Required
    --------
    -i, --input      Trajectory files
    -t, --topology   The prmtop files associated with the inputed
                     trajectory
    -o, --outname    Name given to the put files.


    Optional
    --------
    -r, --range      Selects frames based on a starting and ending
                     index position [default: None]
    -s, --stride     Loads every nth frame into the program
                     [default: 1]
    -f, --format     The format of the files being written out
                     [default: pdb] [choices: pdb, nc]

    setting
    -------
    --all_frames     Indicates to take account all frames between
                     two index positions

    mode
    ----
    --traj2pdb       Converts selected frames into pdbfiles
    --trajslice      Returns a sliced trajectory based on your
                     selected range
    --create_rst     Creates an rst file
                           """))
    pass


if __name__ in '__main__':

    # help and version
    if len(sys.argv) == 1:
        help_message()

    elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
        help_message()

    # setting up mutli thread enviorment
    os.environ['OMP_NUM_THREADS'] = '2'
    parser = argparse.ArgumentParser()

    # labling the types of argument option styles 
    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')
    mode = parser.add_argument_group('Types of Modes')
    setting = parser.add_argument_group('Settings')

    required.add_argument('-i', '--input', type=str, required=True, help="Trajectory file")
    required.add_argument('-t', '--topology', type=str, required=True, help="Topology file")
    required.add_argument('-o', '--outname', type=str, required=True, help="output name")
    optional.add_argument('-r', '--range', nargs='+', type=int, required=False, default=None)
    optional.add_argument('-s', '--stride', type=int, required=False, default=1, help='process files every nth frame')
    optional.add_argument('-f', '--format', default='pdb', choices=['pdb', 'nc'], type=str, required=False, help="output name")
    setting.add_argument('--all_frames', required=False, action='store_true', default=False)
    mode.add_argument('--traj2pdb', required=False, action='store_true', default=False)
    mode.add_argument('--trajslice', required=False, action='store_true', default=False)
    mode.add_argument('--create_rst', required=False, action='store_true', default=False)
    args = parser.parse_args()

    # loading data into memory
    input_data = loader(args.input, args.topology, args.stride)

    if args.traj2pdb is True:
        traj2pdb(input_data, args.outname, indx_list=args.range, all_frames=args.all_frames)

    elif args.trajslice is True:
        slicetraj(input_data, args.outname,  args.range, fmt=args.format)

    elif args.create_rst is True:
        if args.all_frames is True:
            print('Error: creat_rst does not support frame slicing. Please remove the "-all option"')
            exit()
        else:
            create_rst(input_data, args.outname, args.range)

    else:
        print('MESSAGE: No mode has been selected: Please use the help option to list the documentation of the program')
        exit()
