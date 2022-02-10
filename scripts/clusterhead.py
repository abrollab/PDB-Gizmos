#NOTE: This should be a function in pdbcacluate.py
import os
import sys
import subprocess
import argparse
import pandas as pd 
import numpy as np
import textwrap
import mdtraj

# user made modules 
import molTweaks.debugg.logger 
from molTweaks.debugg.logger import Logger

__version__ = 2.0
# todo list 
# TODO: implement logging system 

def get_clusterhead(pdbFiles, threads):
    """Obtaining the best representing cluster head based on RMSD """ 

    # create logging system
    logger = Logger("clusterhead.log")
    
    # data type checking 
    if not isinstance(pdbFiles, list):
        raise ValueError('The requires a list of pdb files not {}'.format(type(pdbFiles)))

    file_count = len(pdbFiles)
    if file_count < 2:
        raise ValueError('2 or more pdbs are required')
    
    # setting up core enviornment 
    os.environ['OMP_NUM_THREADS'] = '{}'.format(threads)
    logger.log_message("threads used: {}".format(threads))

    # obtaining file names:
    logger.log_new_stage("Saving pdbfile names")
    file_names = []
    for file_name in pdbFiles:
        abs_path = os.path.abspath(file_name)
        f_name = abs_path.split('/')[-1]
        file_names.append(f_name)
        
    logger.log_new_stage("calculating rmsd")
    pdb_list = mdtraj.load(pdbFiles)
    raw_rmsd_data = {}
    for frame_num in range(pdb_list.n_frames):
        rmsd_row = mdtraj.rmsd(pdb_list, pdb_list, frame=frame_num)
        raw_rmsd_data[pdbFiles[frame_num]] = rmsd_row * 10 # stores pdb_file_name : rmsd data
        
    # creating a dataframe and search for representing clusterhead 
    data_frame = pd.DataFrame(raw_rmsd_data, index=file_names, columns=file_names)
    avg_dataframe = data_frame.mean()

    logger.log_message("These are the top 5 lowest rmsd values associated with each structure")
    
    print("Message: These are the top 5 lowest rmsd values associated with each structure")
    logger.log_message(str(avg_dataframe.sort_values(ascending=True).head(5)))
    print(avg_dataframe.sort_values(ascending=True).head(5))

    cluster_head = avg_dataframe.idxmin()
    rmsd_value = avg_dataframe.loc[cluster_head]

    print("Your representing clusterhead is:", cluster_head, rmsd_value)
    logger.log_message("Your representing clusterhead is {} rmsd: {:.3f}:".format(cluster_head, rmsd_value))

    logger.close_log()

def help_message():
    print(textwrap.dedent("""
    #######################
    Clusterhead version: {}
    #######################
    
    [Summary]
    -----------
    Program that searches for the best represented representing structure 
    with in a structure based on RMSD
    
    [Use Case]
    ----------
    python clusterhead.py -i *.pdb 
    
    [Required Arguments]
    -i, --input     List of all trajectories being sampled 
    
    [Optional Arguments]
    -t, --threads   Number of treads conducting the calculations
                          
                          """.format(__version__)))
    sys.exit()


if __name__ in '__main__':
   
   # creating help message: 
    if len(sys.argv) == 1:
       help_message()
    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        help_message()
    elif sys.argv[1] == '-v' or sys.argv[1] == '--version':
        print('Clusterheader version: {}'.format(__version__))

    # CLI arguments 
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('Required Options')
    optional = parser.add_argument_group('Optional Arguments')
    required.add_argument('-i', '--input', nargs='+', required=True)
    optional.add_argument('-t', '--threads', type=int, required=False, default=4)
    args = parser.parse_args()
    get_clusterhead(args.input, args.threads)
