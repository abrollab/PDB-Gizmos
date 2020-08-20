################################################################################
# seedpicker.py 2.0 presents an new execute overhall in order to increase
# performance 
# 
# This verision will provide better debugging, performance, and user interface
# Below is the todo list that is required. 
#
# TODO: user made error handling for better debugging of the programs 
#
# TODO: implement cut of value for declarting if an outlier seed is found 
#
# TODO: implement an interactive session when creating the .in file 
#
# TODO: The seedpicker should only accept orignal trajectories
#
# TODO: Once the original trajectory is read, attempt to preprocess it by removing 
#       the water and lipid molecules 
#
# TODO: The trajectories should be processed through cpptraj where the lipids and
#       the solvent is removed. Those also results in creating a new prmtop file 
#       of the stripped system. 
################################################################################
#!/home/programs/anaconda3/bin/python
import argparse
import textwrap
import sys
import os
import shutil
import numpy as np
import pandas as pd 
import mdtraj as md 

# Package modules 
import molTweaks.debugg 
from molTweaks.debugg.logger import Logger
from molTweaks.handler.writer import CpptrajWriter

def get_labled_data(infile, subgroup=False):
    """ Parses the traj input file and creates a dictionary of data"""

    print(f'MESSAGE: Loading input file {infile}\n')

    # saving all the laveled data
    with open(infile, 'r') as f_input:
        raw_input = []
        for line in f_input:
            raw_data = line.strip()
            raw_input.append(raw_data)

    traj_data = [raw_input[i:i + 2] for i in range(0, len(raw_input), 2)]

    # converting sub list into a dictionary
    labled_data = {}
    for data in traj_data:
        subgroup_name = data[0]
        traj_list = data[1:]
        for trajs in traj_list:
            ntrajs = trajs.split(',')
            labled_data[subgroup_name] = ntrajs

    return labled_data

#NOTE: On hold for now 
#TODO: Takes in orgiinal traj --> creates a  (prepreocessed) folder --> use that folder for ananlysis 
def preprocess_trajs(trajs, traj_path, cpptrajfile="pre_cpptraj.in"):
    """ Requires paths of the selected trajectories and strips both the water and 
    lipids from the trajectory. """

    # create a directory for preprocessed trajs 
    cwd = os.getcwd()
    os.mkdir('preprocessed')
    
    # name of the new trajs 
    ai_name = "ai_{}".format(traj_name)
    strp_name = "strp_{}"
    # instanciating handler 
    cpp_writer = CpptrajWriter()

    # execute command 
    cpp_writer.write_autoimg()
    pass


def traj_to_rst(stage_data, topology, labled_trajnames, stride):
    """ Interally creates an cpptraj.in file for creating rst files from selected frames"""

    print('Message: writting .rst files')

    for struct_type, subgroup, frame in stage_data:

        # using the path to trajectory in order to get the name and rename it
        new_name = str(labled_trajnames[subgroup].split(
            '/')[0]).replace('.nc', '')

        with open("cpptraj.in", 'w') as cppinfile:
            cppinfile.write('parm {}\n'.format(topology))
            cppinfile.write('trajin {} {} {}\n'.format(
                labled_trajnames[subgroup], frame, frame))
            cppinfile.write('trajout {}_{}_frame{}.rst restart\n'.format(
                struct_type, new_name, frame * stride))
            cppinfile.write('go')
            cppinfile.close()  # must be explicility closed or the data will never be written out

            # invoking cpptraj
            print("MESSAGE: writting {} frame: {} as rst file".format(new_name, frame))
            cpptraj_cmd = 'cpptraj -i cpptraj.in'.split()
            # NOTE: prevents error when testing
            # subprocess.run(cpptraj_cmd, shell=False)


# NOTE: trajectories are the non stripped ones to extract rst
def traj_to_pdb(stage_data, labeled_trajnames, labeled_trajs, verbose=False):
    """ Converts the selected frames into pdb files """
    
    for struct_type, subgroup, frame_num in stage_data:
        sel_traj = labeled_trajs[subgroup][frame_num]
        sel_trajname = labeled_trajnames[subgroup].split('/')
        
        # creating new name
        new_trajname = str(sel_trajname[-1]).replace(".nc", "")

        # TODO: Add some user defined error handling here 
        try:
            pdbfile_name = '{}_{}_{}_{}.pdb'.format(struct_type, new_trajname, subgroup, frame_num)
            sel_traj.save_pdb(pdbfile_name)
            pdbout_msg = "MESSAGE: {} frame {} has been converted to: {} !".format(new_trajname, frame_num, pdbfile_name )
            if verbose is True:             
                sys.stdout.write(pdbout_msg + '\n')
        except:
            # NOTE: USer error shold be hereveeer
            print(f'FAILED: {new_trajname} frame {frame_num} conversion failed.')
            continue


def get_distance(stage_data, traj_paths, merged_df, include_soln=False): 

    sys.stdout.write("\n" + "Obtaining Distances of each outlier structure" + "\n")
    
    soln_stage_data = [tuple([stage, tag, frame]) for stage, tag, frame in stage_data if 'soln' in stage] # NOTE: This is not used yet 
    outl_stage_data = [tuple([stage, tag, frame]) for stage, tag, frame in stage_data if 'outl' in stage]
    unique_tags = ["{}_{}".format(tag, frame) for stage, tag, frame in outl_stage_data]
    stage = stage_data[0][0]

    # edit the data frame 
    unique_row_id = merged_df.columns[2:]
    merged_df.loc[unique_row_id]
    
    # calculating distances 
    for idx_itag in range(len(unique_tags) - 1):
        for idx_jtag in range(idx_itag + 1, len(unique_tags)):
            
            # for  stdout pruposes converts "g0t1_1" --> ("g0t0m", 1)
            i_tag, i_frame = tuple(unique_tags[idx_itag].split('_'))
            j_tag, j_frame = tuple(unique_tags[idx_jtag].split('_'))

            # gets name of traj converting "path/to/tragname.nc" --> "tragname"
            i_name = str(traj_paths[i_tag].split('/')[-1]).replace('.nc', '')
            j_name = str(traj_paths[j_tag].split('/')[-1]).replace('.nc', '')
            
            # indices uwed for look up in data 
            struct_i = unique_tags[idx_itag]
            struct_j = unique_tags[idx_jtag] 

            # Creating rmsd series 
            series = pd.Series(merged_df[struct_i].values, index=merged_df.index.tolist())      
            rmsd = series.loc[struct_j].round(3) 

            # writting results 
            sys.stdout.write("{0}_{1} frame {2} ---- {0}_{3} frame {4} rmsd: {5}".format(stage, i_name, i_frame, j_name, j_frame, rmsd) + "\n")


def select_atoms(top_file, atom_selection, atomtype, verbose=False):
    """ Returns 1D array of atom ids that cooresponds to the inputed selection """

    prmtop = md.load_topology(top_file)

    # if not slection is provided only use all atoms and prefered type
    if atom_selection is None: 
        if atomtype == "CA":
            atom_select_query = "name {}".format(atomtype) 
            selected_atoms = prmtop.select(atom_select_query) 
           
           # stdout purposes 
            if verbose is True: 
                sys.stdout.write("Selected Atoms: " + "\n")
                sys.stdout.write(atom_select_query + "\n")
                sys.stdout.write(str(selected_atoms) + "\n") 

            return selected_atoms

        else: 
            selected_atoms = prmtop.select(atomtype)

            # stdout prupose 
            if verbose is True: 
                sys.stdout.write("Selected Atoms: " + "\n")
                sys.stdout.write(str(selected_atoms) + "\n") 

            return selected_atoms

    if atom_selection is not None and atomtype == "CA":
        select_query = "name {} and ( ".format(atomtype) + "{} )".format(atom_selection)
    else:
        select_query = "{} and ( ".format(atomtype) + "{} )".format(atom_selection)
    
    atom_sel = prmtop.select(select_query)

    # stdout purpose 
    if verbose is True:
        sys.stdout.write("Selected Atoms: " + "\n")
        sys.stdout.write(select_query + "\n")
        sys.stdout.write(str(atom_sel) + "\n") 
    return atom_sel 


def get_rmsd(traj, topology, sel_atoms=None):
    """ returns a geneorator when calculating rmsd from trajectories """
    if not isinstance(traj, md.Trajectory):
        prmtop = md.load_topology(topology)
        traj = md.load(traj, top=prmtop, stride=1)

    for frame_idx in range(traj.n_frames):
        rmsd = np.round(md.rmsd(traj, traj, frame=frame_idx, atom_indices=sel_atoms) * 10, 3)
        yield rmsd

    

# Main algorithim 
def seedpicker(labled_data, topfile, n_cores, stride, verbose=False, sel_atoms=None):
    """Main algorithim consisting of 3 stages for finding outliers and soln i
    structos"""

    # ---------------
    # Collecting data
    # ---------------

    # creating a log file
    seedpicker_log = Logger('seedpicker.log')
    
    # setting OPM threads 
    os.environ['OMP_NUM_THREADS'] = '{}'.format(n_cores)

    # loading the trajectories topology
    prmtop = md.load_topology(topfile)

    raw_trajs = {}  # {'subgroup : 'traj_object'}
    traj_paths = {}  # {'subgroup', 'path/traj_name'} # subgroup andp path/of/trajectory
    traj_namelist = [] 

    # loading trajectories
    seedpicker_log.log_new_stage('Loading Trajectories')
    start_message = 'MESSAGE: Loading trajectories with a stride of {}..\n'.format(stride)
    sys.stdout.write(start_message)
    seedpicker_log.log_message(start_message)

    for subgroup, traj_nlist in labled_data.items():
        count_traj = 0
        for trajname in traj_nlist:
            t_name = trajname.strip()
            # getting trjectory object
            traj_obj = md.load(t_name, top=prmtop, stride=stride)             
            data_info = f'{subgroup}t{count_traj}'
            traj_namelist.append(traj_obj)
            raw_trajs[data_info] = traj_obj
            traj_paths[data_info] = t_name
            trajin_log = f'Trajectory: {t_name} {traj_obj.n_frames} frames'
            seedpicker_log.log_message(trajin_log)

            if verbose is True:
                sys.stdout.write(trajin_log + '\n')

            count_traj += 1

    # -------------------------------
    # stage 1: Merge all trajectories
    # -------------------------------
    s1_message = 'Stage 1: Finding Global outlier and solution structure'
    sys.stdout.write("\n" + s1_message + "\n")
    seedpicker_log.log_new_stage(s1_message)

    # merging trajectories 
    merged_trajs = md.join(traj_namelist)

    # Calculating rmsds
    # merged_raw_rmsd_data = []
    # for idx in range(merged_trajs.n_frames):
    #     m_rmsd_data = np.round(md.rmsd(merged_trajs, merged_trajs, frame=idx, atom_indices=sel_atoms) * 10, 3)
    #     merged_raw_rmsd_data.append(m_rmsd_data)
    
    # NOTE: geneorator placed here
    merged_raw_rmsd_data = get_rmsd(merged_trajs, prmtop)
    

    # creating pandas df for avg and raw 
    col_row_indx = []
    for tag, traj_obj in raw_trajs.items():
        for frame_num in range(traj_obj.n_frames):
            tag_frame = '{}_{}'.format(tag, frame_num)
            col_row_indx.append(tag_frame)

    # creatign data frames 
    raw_rmsd_df = pd.DataFrame(merged_raw_rmsd_data, index=col_row_indx, columns=col_row_indx)
    avg_rmsd_df = pd.DataFrame(raw_rmsd_df.mean().round(3), columns=["avg_rmsd"])

    # writing mereged dataframe 
    raw_rmsd_df.to_csv('raw_rmsd_df.csv')
    avg_rmsd_df.to_csv('avg_rmsd_df.csv')

    # finding both highest and lowest average rmsd ['', 'tag_frame', 'rmsd']
    s1_results = []
    global_soln_data = str(avg_rmsd_df[avg_rmsd_df['avg_rmsd'] == avg_rmsd_df['avg_rmsd'].min()]).split()[-2::]
    global_outl_data = str(avg_rmsd_df[avg_rmsd_df['avg_rmsd'] == avg_rmsd_df['avg_rmsd'].max()]).split()[-2::]


    # extracting unique tag and frame 
    soln_tag, soln_frame = tuple(global_soln_data[0].split('_')) 
    outl_tag, outl_frame = tuple(global_outl_data[0].split('_'))
    
    g_soln_trajname = traj_paths[soln_tag].split('/')[-1]
    g_soln_rmsd = float(global_soln_data[1])
    g_soln_traj_path = traj_paths[soln_tag]
    
    g_outl_trajname = traj_paths[outl_tag].split('/')[-1]
    g_outl_rmsd = float(global_outl_data[1])
    g_outl_traj_path = traj_paths[outl_tag]

    # stdout results and saving into log
    s1_soln_result = "solution structure: {}, frame: {}, rmsd: {:.3f}, path: {}".format(g_soln_trajname, soln_frame, g_soln_rmsd, g_soln_traj_path) 

    s1_outl_result = "outlier structure: {}, frame: {}, rmsd: {:.3f}, path: {}\n".format(g_outl_trajname, outl_frame, g_outl_rmsd, g_outl_traj_path)

    # writting it to a log file 
    s1_top_rmsd = str(avg_rmsd_df.sort_values(by=['avg_rmsd'], ascending=False).round(3).head(10)) + '\n'
    seedpicker_log.log_message(s1_soln_result)
    seedpicker_log.log_message(s1_outl_result)
    seedpicker_log.log_message("\n" + s1_top_rmsd)

    if verbose is True:
        sys.stdout.write(s1_soln_result + '\n')
        sys.stdout.write(s1_outl_result + '\n')
        sys.stdout.write('Top 10 Highest rmsd\n')
        sys.stdout.write(s1_top_rmsd + '\n')

    # appending results to a list 
    s1_results.append(tuple(['s1_soln', soln_tag, int(soln_frame)]))
    s1_results.append(tuple(['s1_outl', outl_tag, int(outl_frame)]))

    # write the pdbs 
    traj_to_pdb(s1_results, traj_paths, raw_trajs, verbose=verbose)
     
    # write the rst frome oroginal trajectory 
    traj_to_rst(s1_results, prmtop, traj_paths, stride) 
    
    # ---------------------------------------
    # stage 2: Searching for local structures  
    # ----------------------------------------

    # Logging new stage 
    s2_message = "Stage 2: Locating local outliers and solution structures"
    sys.stdout.write(s2_message + '\n')
    seedpicker_log.log_new_stage(s2_message)
    
    # using merged matrix to find local trajectories by seperating them 
    s2_results = []
    for tag in traj_paths.keys():
        # filters data from mereged avg df and extract selected tagnames 
        all_row_indx = avg_rmsd_df.index.tolist()
        filter_indx = [r_idx for r_idx in all_row_indx if r_idx.startswith(tag)]

        #creating avg rmsd df per trajectory
        local_df = avg_rmsd_df.loc[filter_indx]
        
        # finding local solution and outlier 
        local_soln_data = local_df[local_df['avg_rmsd'] == local_df['avg_rmsd'].min()].iloc[0]#.tolist() # .iloc[0]
        local_outl_data = local_df[local_df['avg_rmsd'] == local_df['avg_rmsd'].max()].iloc[0]#.tolist() # .iloc[0].values.

        # extracting unique tag and frame 
        traj_path_name = traj_paths[tag]
        traj_name = traj_paths[tag].split('/')[-1]

        # get the unique tag and split it to get he frame --> g0t0_1 -> [g0t0, 1]
        l_soln_frame = local_soln_data.name.split('_')[-1]
        l_outl_frame = local_outl_data.name.split('_')[-1]

        # getting rmsd values for both solution and outlier structure
        l_soln_rmsd = round(float(local_soln_data.values), 3)
        l_outl_rmsd = round(float(local_outl_data.values), 3)
       
        # formating results for stdout  
        s2_soln_result = "solution structure: {}, frame: {}, rmsd: {:.3f}, path: {}".format(traj_name, l_soln_frame, l_soln_rmsd, traj_path_name) 
        s2_outl_result = "outlier structure: {}, frame: {}, rmsd: {:.3f}, path: {}\n".format(traj_name, l_outl_frame, l_outl_rmsd, traj_path_name)
        s2_top_rmsd = str(local_df.sort_values(by=['avg_rmsd'], ascending=False).round(3).head(10)) + '\n'
        
        # logging results 
        seedpicker_log.log_message(s2_soln_result)
        seedpicker_log.log_message(s2_outl_result)
        seedpicker_log.log_message('top RMSDs of {}'.format(traj_name))
        seedpicker_log.log_message("\n" + s2_top_rmsd)

        # # appending results into a list 
        s2_results.append(tuple(['s2_soln', tag, int(l_soln_frame)]))
        s2_results.append(tuple(['s2_outl', tag, int(l_outl_frame)]))

        # # message shown in command line
        if verbose is True:
            sys.stdout.write(s2_soln_result + '\n')
            sys.stdout.write(s2_outl_result + '\n')
            sys.stdout.write("Resulting rmsds for each trajectory \n")
            sys.stdout.write(s2_top_rmsd + '\n')
            
    
    # write the pdbs 
    traj_to_pdb(s2_results, traj_paths, raw_trajs, verbose=verbose)
     
    # write the rst frome oroginal trajectory 
    traj_to_rst(s2_results, prmtop, traj_paths, stride) 


    # ---------------------------
    # stage 3: subgrouping search 
    # ---------------------------
    s3_message = "Stage 3: subgroup searching for outliers and solution structures"
    sys.stdout.write(s3_message + '\n')
    seedpicker_log.log_new_stage(s3_message)
    
    groups = []
    s3_df_idx = avg_rmsd_df.index.tolist()
    for tag in s3_df_idx:
        group = tag[0:2]
        if group not in groups:
            groups.append(group)

    s3_results = []
    for group in groups: 
        filter_indx = [indx for indx in avg_rmsd_df.index.tolist() if indx.startswith(group)]
        s3_group_df = avg_rmsd_df.loc[filter_indx].reset_index()
    

        # obtain solution and outlier data 
        subg_soln_struct = s3_group_df[s3_group_df['avg_rmsd'] == s3_group_df['avg_rmsd'].min()].iloc[0].values.tolist()
        subg_outl_struct = s3_group_df[s3_group_df['avg_rmsd'] == s3_group_df['avg_rmsd'].max()].iloc[0].values.tolist()

        #obtaining tag and frame 
        soln_tag, soln_frame = tuple(subg_soln_struct[0].split('_'))
        outl_tag, outl_frame = tuple(subg_outl_struct[0].split('_'))

        #extracting all results for std.out purposes 
        subg_soln_trajname = str(traj_paths[soln_tag].split("/")[-1].replace(".nc", ""))
        subg_soln_rmsd = round(float(subg_soln_struct[1]), 3)
        sub_soln_path = traj_paths[soln_tag] 
        
        subg_outl_trajname = str(traj_paths[outl_tag].split("/")[-1].replace(".nc", ""))
        subg_outl_rmsd = round(float(subg_outl_struct[1]), 3)
        sub_outl_path = traj_paths[outl_tag] 

        # loggin results 
        s3_soln_result = "solution structure: {}, frame: {}, rmsd: {:.3f}, path: {}".format(subg_outl_trajname, int(soln_frame), subg_soln_rmsd, sub_soln_path) 
        s3_outl_result = "outlier structure: {}, frame: {}, rmsd: {:.3f}, path: {}\n".format(subg_outl_trajname, int(outl_frame), subg_outl_rmsd, sub_outl_path)
        s3_top_rmsd_df = str(s3_group_df.sort_values(by=["avg_rmsd"], ascending=False))

        seedpicker_log.log_message(s3_soln_result)
        seedpicker_log.log_message(s3_outl_result)
        seedpicker_log.log_message("\n" + s3_top_rmsd_df)
        
        # saving results 
        s3_results.append(tuple(['s3_soln', soln_tag, int(soln_frame)]))
        s3_results.append(tuple(['s3_outl', outl_tag, int(outl_frame)]))
        
        if verbose is True: 
            sys.stdout.write(s3_soln_result + "\n")
            sys.stdout.write(s3_outl_result + "\n")
            sys.stdout.write("Resulting rmsds for each group" + "\n")
            sys.stdout.write(s3_top_rmsd_df + "\n")
            

    # TODO: do this later 
    # write the pdbs 
    traj_to_pdb(s3_results, traj_paths, raw_trajs, verbose=verbose)
     
    # write the rst frome oroginal trajectory 
    traj_to_rst(s3_results, prmtop, traj_paths, stride) 

    # Obtaining ditances 
    get_distance(s3_results, traj_paths, raw_rmsd_df, include_soln=False)
    seedpicker_log.close_log('Ending Process')

    
def help_message():

    print(textwrap.dedent("""
    [Summary]

    Seedpicker.py is a brute-force algorithm that searches for a specific
    conformation that deviates greatly from other snapshots in a given
    trajectory.

    This program captures intrinsic and least populated conformations
    which could serve as aviable starting point to explore the
    conformational landscape.

    [Use Case Example]

    seedpicker.py -i traj_list.in -p 5g53_100ns_md.prmtop

    [Required arguments]:
    -i, --input             Input file containing all groupings of the
                            trajectories

    -t, --topology         The topology file prmtop


    [Optional arguments]:
    -c, --cores             Number of cores used for rmsd calculations
                            [default: 4]

    -s, --stride            Stide of frames that will be processed
                            [default: 1]

    -x, --cutoff            Cutoff value indicating if a new outlier is
                            found in the trajectories [default: 2.00]

    -o, --output            Write an output to the current directory. One
                            can select either matrix binary or csv. If
                            [Default: csv] [Choices: csv, matrix]

    -v, --verbose           Displays 20 lines of the rmsd data in each
                            stage
                            
    -r, --resids            Selection of residues that will be used for 
                            for RMSD calculations. If none is specified,
                            all atoms will be used for calcutions.
                            [default: None]

    -a, --atomtype          Refers to what atoms the user wants to use
                            when calculating for RMSD. 
                            [default: CA]
                            [choices: all, CA, backbone, sidechain, protein]
    """))
    sys.exit()


if __name__ in '__main__':

    # NOTE: This class is called by the argparser to transform the indices into a readable selection 
    class ParseSelection(argparse.Action):
        """ converts the use specfied selection to the appropiate format for rmsd calculations with selected atoms"""
        def __call__(self, parser, namespace, string, option_string=None, atom_type="CA"):
            selections = string.split(',')

            sel_list = []
            for res_value in selections:
                if '-' in res_value:
                    add_to = res_value.replace("-", " to ")
                    to_str = "resid " + add_to
                    sel_list.append(to_str)
                else:
                    single_resid = "resid " + res_value
                    sel_list.append(single_resid) 

            new_string = " or ".join(sel_list)             

            # sets the appropiate formate for atom selection 
            setattr(namespace, self.dest, new_string)
    
    if len(sys.argv) == 1:
        help_message()

    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        help_message()

    # TODO: implement error handler for missing dependency 
    # checkin if the user has cpptraj executable
    if shutil.which('cpptraj') is None:
        print('ERROR: Missing dependency: Cpptraj')
        raise MissingDependency("Cpptraj is not found in your system") # TODO: create a custome handler
        exit()

    # CLI arguments
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')
    required.add_argument('-i', '--input', type=str, required=True)
    required.add_argument('-t', '--topology', type=str, required=True)
    optional.add_argument('-c', '--cores', type=int, default=4, required=False)
    optional.add_argument('-s', '--stride', type=int, required=False, default=1)
    optional.add_argument('-x', '--cutoff', type=float, required=False, default=2.00)
    optional.add_argument('-o', '--output', type=str, required=False, default=False)
    optional.add_argument('-f', '--format', type=str, required=False, default='csv', choices=['csv', 'matrix'])
    optional.add_argument('-v', '--verbose', action='store_true', default=False, required=False)
    optional.add_argument('-r', '--resids', type=str, default=None, action=ParseSelection, required=False)
    optional.add_argument('-a', '--atomtype', type=str, default=None, choices=['all', 'CA', 'backbone', 'protein', 'sidechain'], required=False)
    args = parser.parse_args()

    # invoking function with  arguments
    labled = get_labled_data(args.input)
    
    # checks if there is a resid if so, reutrns a 1D array of atom ids 
    if args.resids is not None:
        selected_atoms = select_atoms(args.topology, args.resids, args.atomtype, args.verbose)
    elif args.resids is None and args.atomtype is not None: 
        selected_atoms = select_atoms(args.topology, args.resids, args.atomtype, args.verbose)
    else:
        selected_atoms = None
        
    seedpicker(labled, args.topology, args.cores, args.stride, args.verbose, selected_atoms)
