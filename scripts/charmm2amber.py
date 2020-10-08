import sys
import subprocess
import glob
import textwrap
import argparse
import os

# version 
__version__ = '2.2.10'

def extract_charmm_files(charmm_file: str, charmm_outdir: str):
    """
    Function that extracts the CHARMM-GUI files. Only support tar and tgz files
    """

    if charmm_file.endswith('.tar'):
        tarcom = f'mkdir {charmm_outdir} && tar xf {charmm_file} -C {charmm_outdir} --strip-components 1'
        os.system(tarcom)
    elif charmm_file.endswith('.tgz'):
        tarcom = f'mkdir {charmm_outdir} && tar xzf {charmm_file} -C {charmm_outdir} --strip-components 1'
        os.system(tarcom)
 
    
def getSystem(charmmFile, sysname, sysres, overwrite, type="membrane"):
    '''
    action:
    Obtains .pdb, .rst7, .parm files from charmm file and renames it to appropiate extensions required for the setup_amber.pl script.

    input:
    requires arguments from the user that specifies the system name and number of residues

    output:
    A directory containing the necessary files to start AMBER simulations.
    '''
    # getting current dirrectory
    wdir = os.getcwd()

    # checks if the file exists
    if not os.path.exists(charmmFile):
        raise FileNotFoundError(f"The file {args.input} does not exists. Please check the name of your input file")

    # Overwrite conditional
    charmm_dir = '{}_CHARMM-GUI'.format(sysname)
    if os.path.exists(charmm_dir) and overwrite == False:
        reset(wdir, sysname)
        raise FileExistsError(f'The directory {charmm_dir} already exists. Please execute this porgram in a new directory or use the "-o" options to overwrite the existing files')
    elif os.path.exists(charmm_dir) and overwrite:
        print('MESSAGE: Overwriting previous CHARMM-GUI directories...')
        subprocess.run(f'rm -rf {charmm_dir}', shell=True)

    # checks if the amber file exists
    amber_dir = f'{sysname}_AMBER'
    if os.path.exists(amber_dir) and overwrite == False:
        raise FileExistsError(f'The directory {amber_dir} already exists. Please execute this program in a new diretiory or use -o to overwrite the existing directory')
    elif os.path.exists(amber_dir)  and overwrite:
        print('MESSAGE: Overwriting previous AMBER directories...')
        subprocess.run(f'rm -rf {amber_dir}', shell=True)

    # extraction process
    extract_charmm_files(charmmFile, charmm_dir)

    # making the directories
    print('MESSAGE: Creating folders...')
    os.chdir(charmm_dir)
    os.chdir('amber')
    print('MESSAGE: obtaining files for MD simulations...')

    # selecting the correct pdb file depending on which force field was selected
    if type == "membrane":
        if os.path.exists('step5_charmm2amber.complete.pdb'):
            print('DETECTED: CHARMM-GUI output contains the AMBER force field')
            getFilesCmd = "cp step5_charmm2amber.complete.pdb step5_charmm2amber.rst7 step5_charmm2amber.parm7 {}".format(wdir)
            subprocess.run(getFilesCmd.split(), shell=True)
        else:
            print('DETECTED: CHARMM-GUI output contains the CHARMM force field')
            getFilesCmd = "cp step5_input.pdb step5_input.rst7 step5_input.parm7 {}".format(wdir)
            subprocess.run(getFilesCmd.split(), shell=True)
    
    # TODO: add support for solvated models 
    elif modle_type == "solvate":
    #------------------------------ 
    # extra block code for solvate
    #------------------------------ 
    subprocess.run(getFilesCmd, shell=True)
    os.chdir(wdir)
    os.mkdir(amber_dir)

    reNameCmd = f"mv step5*pdb {sysname}_md.pdb ; mv  step5*parm7 {sysname}_md.prmtop ; mv step5*rst7 {sysname}_md.inpcrd"
    subprocess.run(reNameCmd, shell=True)

    # applying residue check feature
    syspdb = f'{sysname}_md.pdb'
    res_check = residueCheck(syspdb)  # returns {int} --> number of resudes of system
    if sysres is None or sysres == res_check:  # default is set to none in order to use res_check value
        amber_cmd = f' amber_run_setup.pl -s {sysname} -r {res_check}'
        subprocess.run(amber_cmd, shell=True)
        mv_all = f'mv {sysname}_md.pdb {sysname}_md.inpcrd {sysname}_md.prmtop {sysname}*.in {sysname}*.pbs {sysname}*.bash  {charmm_dir} {amber_dir}'
        subprocess.run(mv_all, shell=True)
        print("MESSAGE: Charmm2amber is complete!")

    ############################
    # User respnonses start here
    ############################
    elif res_check != sysres:  # use elif res_check == rescheck is false --> use int
        print('MESSAGE: Resiude check: FAILED',
        '\nWARNING: The amount of residues specified does not match with the total amount of CA atoms obtained from the pdb file.',
        f'\n\nThis is the correct amount: {res_check}')

        # user reponse to custome resiude count
        response_count = 0
        while True:
            usr_res_response = input(f'\nDo you still wish to use {sysres} as your residue count? (Y/n): ')

            # If the response is yes, amber files will be generated
            if usr_res_response.lower() == 'yes' or usr_res_response.lower() == 'y':
                print(f'MESSAGE: Using {sysres} reisudes count to build your simulation ...')
                amber_cmd = f' amber_run_setup.pl -s {sysname} -r {sysres}'
                subprocess.run(amber_cmd, shell=True)
                mv_all = f'mv {sysname}_md.pdb {sysname}_md.inpcrd {sysname}_md.prmtop {sysname}*.in {sysname}*.pbs {sysname}*.bash  {charmm_dir} {amber_dir}'
                subprocess.run(mv_all, shell=True)
                print("Charmm2amber is complete!")
                exit()

            # if the response no, the program will ask for a different value
            elif usr_res_response.lower() == 'no' or usr_res_response.lower() == 'n':

                # asking if they want the default
                default_attempts = 0
                while True:

                    # attempts checker
                    if default_attempts == 3:
                        print('too many failed attempts. Exiting program')
                        reset(wdir, sysname)
                        exit()

                    # asking the user if the they want to use the default residue count
                    default_response = input(f'\nWill you like to use the default number of residues of your system? (Y/n): ')

                    # if the response is yes, create the amber files
                    if default_response.lower() == 'y' or default_response.lower() == 'yes':
                        print(f'Using {res_check} residues to buld your simulation files')
                        amber_cmd = f' amber_run_setup.pl -s {sysname} -r {res_check}'
                        subprocess.run(amber_cmd, shell=True)
                        mv_all = f'mv {sysname}_md.pdb {sysname}_md.inpcrd {sysname}_md.prmtop {sysname}*.in {sysname}*.pbs {sysname}*.bash  {charmm_dir} {amber_dir}'
                        subprocess.run(mv_all, shell=True)
                        print("Charmm2amber is complete!")
                        exit()

                    # if the response is no, ask for a new input
                    elif default_response.lower() == 'n' or default_response.lower() == 'n':
                        new_count_attempts = 0
                        while True:
                            try:
                                # attempt checker
                                if new_count_attempts == 3:
                                    print('MESSAGE: Too many failed attempts. Exiting program.')
                                    reset(wdir, sysname)
                                    exit()

                                # user inputs new res count. Does not save value if the new value is bigger than res_check's
                                new_count = int(input('Please enter your new reisude count: '))
                                if new_count > res_check:
                                    print(f'WARNNING: The number of resiudes provided exceeds the total amount of reisudes that your system has! \nYour system has {res_check} residues!')

                                else:
                                    print(f'using {new_count} resiudues to build your simulation files.')
                                    amber_cmd = f' amber_run_setup.pl -s {sysname} -r {new_count}'
                                    subprocess.run(amber_cmd, shell=True)
                                    mv_all = f'mv {sysname}_md.pdb {sysname}_md.inpcrd {sysname}_md.prmtop {sysname}*.in {sysname}*.pbs {sysname}*.bash  {charmm_dir} {amber_dir}'
                                    subprocess.run(mv_all, shell=True)
                                    print("Charmm2amber is complete!")
                                    exit()

                            except ValueError:
                                print('ERROR: The input you have provided is not an integer. Please enter an integer.')
                                new_count_attempts += 1

                    else:
                        print('MESSAGE: Please enter a valid response')
                        default_attempts += 1

                attempts = 0
                while True:

                    # 3 fail attempts causes the program to reset and exit
                    if attempts == 3:
                        print('MESSAGE: Too many failed attempts. Exiting program.')
                        reset(wdir, sysname)
                        exit()

                    try:
                        new_res_count = int(input('Please enter your new reisude count: '))

                        if new_res_count > res_check:
                            print(f'WARNING: The value entered {new_res_count} is larger that the system: {res_check}',
                                  '\nPlease enter an appropiate value.')

                        print(f'MESSAGE: Using {new_res_count} reisudes count to build your simulation ...')
                        amber_cmd = f' amber_run_setup.pl -s {sysname} -r {new_res_count}'
                        subprocess.run(amber_cmd, shel=True)            
                        mv_all = f'mv {sysname}_md.pdb {sysname}_md.inpcrd {sysname}_md.prmtop {sysname}*.in {sysname}*.pbs {sysname}*.bash  {charmm_dir} {amber_dir}'
                        subprocess.run(mv_all, shell=True)
                        print("Charmm2amber is complete!")
                        exit()

                    except ValueError:
                        print('MESSAGE: The input you have provided is not an integer. Please enter an integer.')
                        attempts += 1

            # 3 fail attempts causes the program to reset and exit
            elif response_count == 3:
                print('MESSAGE: Too many failed attempts. Exiting program.')
                reset(wdir, sysname)
                exit()

            else:
                print('Invalid response. Please try again.')
                response_count += 1
    else:
        print('Uh oh something went wrong!')
        exit()


def residueCheck(pdbfile: str):
    """
    action:
    checks if number of residues provided == the total of CA atoms in pdb file.

    input:
    requires specified number of residues and it's corresponding pdbfile.

    returns:
    True if user input residue count is equal to the amount of CA atoms
    present in pdbfile. If False, it returns an interger that pertains to the
    correct number of residues of the system.
    """
    print('MESSAGE: Residue check: Counting residues...')
    with open(pdbfile, 'r') as f:
        CA_count = 0
        for data in f:
            lines = data.split()
            if "ATOM" == lines[0] and "CA" == lines[2]:
                CA_count = CA_count + 1

        return CA_count


def reset(working_dir: str, sys_name: str):
    """
    [Summary]:
        - removes the created folders and files during the program if an error occurs.

    [input]
        - wdir {string} => working directory where the charmm2amber was executed

    """
    # get all the files fom the current working directory
    print('MESSAGE: Resetting current process...')
    os.chdir(working_dir)
    rm_files = glob.glob(f'{sys_name}_md.pdb') + glob.glob(f'{sys_name}_md.inpcrd') + glob.glob(f'{sys_name}_md.rst7') + glob.glob(f'{sys_name}_md.parm7') + glob.glob(f'{sys_name}_md.prmtop') 

    # obtaining raw files from
    unamed_files = glob.glob('step5_charmm2amber*pdb') + glob.glob('step5_charmm2amber*inpcrd') + glob.glob('step5_charmm2amber*rst7') + glob.glob('step5_charmm2amber*prmtop') + glob.glob('step5_charmm2amber*parm7')

    labled_dirs = glob.glob(f'{sys_name}_CHARMM-GUI') + glob.glob(f'{sys_name}_AMBER')
    
    all_files = rm_files + unamed_files + labled_dirs
    # iterate the files and check with
    for files in all_files:
        subprocess.run(f'rm -rf {files}', shell=True)


def help_message():
    print(textwrap.dedent("""
    ###########################
    Charmm2amber Version: {}
    ###########################
    
    [ Summary ]
    Charrm2amber is a program that allows the users to create on the fly MD simulation read files.
    The program only requires the compressed files (.tar or .tgz) obtained from CHARMM-GUI and also
    provide a name for the system your are creating.


    [ Use case Example ]
    python charmm2amber.py -i chamm_gui.tgz -s a2a_5g53_active

    Display the help menu (3 ways):
    python charmm2amber.py
    python charmm2amber.py -h
    python charmm2amber.py --help

    [ Help menu ]
    -h, --help          Displays the help message when it appears
    
    -v, --version       Displays the current version installed 

    [ Required Arguments ]
    -i, --input         The compressed files (.tgz or .tar) obtained from CHARMM-GUI

    -s, --sysname       The name of the system that will used in creating the simulation
                        files


    [ Optional Arguments ]
    -t,  --type         Type of model that was produces in CHARMM-GUI. [Default: membrane]
                        [Choices: membrane, solvated]

    -r,  --sysres       The selected range of resid that you want to use for your simulation
                        [default: None]

    -o, --overwrite     Overwrite existing CHARMM-GUI and AMBER
                          """.format(__version__)))
    sys.exit()

if __name__ in '__main__':

    # Displaying help message if no arguments or "-h" "--help" were passed
    if len(sys.argv) == 1:
        help_message()

    elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
        help_message()
        
    elif sys.argv[1] == '--version' or sys.argv[1] == '-v':
        print('charmm2amber {}'.format(__version__))
        sys.exit()

    # creating CLI optional arguments
    parser = argparse.ArgumentParser(add_help=False)
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments ')

    required.add_argument('-i', '--input', type=str, required=True,
                            help="CHARMM-GUI .tgz/.tar output file")
    required.add_argument('-s', '--sysname', type=str, required=True,
                            help="Name of the system")
    optional.add_argument('-r', '--sysres', type=int, nargs='?', required=False, default=None,
                            help='Total number of residues of the system' )
    optional.add_argument('-o', '--overwrite', default=False, action='store_true', required=False,
                              help='Ignores the "FileExistsError" when using the same system name')
    optional.add_argument('-t', '--tpye', type=str,default="membrane", choices=["membrane", "solvated"],
                          required=False, help="Type of model that was created in CHARMM-gui") 
    args = parser.parse_args()

    # executing program
    getSystem(args.input, args.sysname, args.sysres, args.overwrite)
