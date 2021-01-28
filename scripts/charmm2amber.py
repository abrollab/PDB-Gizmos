import os
import sys
import glob
import shutil
import textwrap
import argparse
import subprocess
import urllib.request


# version
__version__ = '2.3.0'


def reset(working_dir, sys_name):
    """
    [Summary]:
        - removes the created folders and files during the program if an error occurs.
    [input]
        - wdir {string} => working directory where the charmm2amber was executed
    """

    # get all the files fom the current working directory
    os.chdir(working_dir)
    rm_files = glob.glob(f'{sys_name}_md.pdb') + glob.glob(f'{sys_name}_md.inpcrd') + glob.glob(f'{sys_name}_md.rst7') + glob.glob(f'{sys_name}_md.parm7') + glob.glob(f'{sys_name}_md.prmtop')

    # obtaining raw files from
    unamed_files = glob.glob('step5_charmm2amber*pdb') + glob.glob('step5_charmm2amber*inpcrd') + glob.glob('step5_charmm2amber*rst7') + glob.glob('step5_charmm2amber*prmtop') + glob.glob('step5_charmm2amber*parm7')
    labled_dirs = glob.glob(f'{sys_name}_CHARMM-GUI') + glob.glob(f'{sys_name}_AMBER')

    all_files = rm_files + unamed_files + labled_dirs

    # iterate the files and check with
    for files in all_files:
        print("overwriting {}".format(files))
        subprocess.run(f'rm -rf {files}', shell=True)


def decompress_charmmfile(charmm_tgz, charmm_outdir):
    """
    Function that extracts the CHARMM-GUI files. Only support tar and tgz files.
    Returns the path to the extracted CHARMM-GUI file
    """
    url = "http://www.charmm-gui.org/?doc=input/download&jobid={}".format(charmm_tgz)
    extracted_file = "{}.tgz".format(charmm_outdir)
    #extract_cmd = 'tar xzf {} -C {} --strip-components 1'.format(charmm_tgz, charmm_outdir).split()

    if charmm_tgz.endswith('.tar') or charmm_tgz.endswith('.tgz'):
        # extracting download tgz file
        print("extracting from {}".format(charmm_tgz))
        shutil.unpack_archive(charmm_tgz, charmm_outdir)

        if not os.path.exists(charmm_outdir):
            raise FileNotFoundError("Extracted CHARMM-GUI directory cannot be found")
        return os.path.abspath(charmm_outdir)

    elif charmm_tgz.isdigit():
        # download tgz file
        print("Using Job ID {} to download CHARMM-GUI file".format(charmm_tgz))
        urllib.request.urlretrieve(url, extracted_file)

        # extracting contents from downloaded file
        print("Extracting contents from {}".format(extracted_file))
        shutil.unpack_archive(extracted_file, charmm_outdir)
        if not os.path.exists(charmm_outdir):
            raise FileNotFoundError("Extracted CHARMM-GUI directory cannot be found")

        return os.path.abspath(charmm_outdir)

    else:
        raise ValueError("Invalid input was provided")

def clean_up(cdir, c_file, amber_dir, charmm_dir):
    """ cleans the envioment where the script was executed and places
    all data in  the amber folder """

    print("Cleaning up environment.")
    os.chdir(cdir)
    shutil.move(c_file, amber_dir)
    shutil.move(charmm_dir, amber_dir)
    print("All data has been moved to: ./{}".format(os.path.relpath(amber_dir)))

def res_count(pdbfile):
    """
    Counts the number of residues in the system.
    Returns (int):
        total number of resiudes.
    """
    print('Obtaining number of residues')
    with open(pdbfile, 'r') as f:
        CA_count = 0
        for data in f:
            lines = data.split()
            if "ATOM" == lines[0] and "CA" == lines[2]:
                CA_count = CA_count + 1
        print("There is a total of {} resiudes in this system".format(CA_count))
        return CA_count


def extract_and_format(charmm_dir, sysname, out_amber_dir):
    """
    Prodcedual function that extracts files within from the CHARMM-GUI
    file and formats it to
    """
    cwd = os.getcwd()
    ext_trans = {
        ".pdb" : ".pdb",
        ".rst7": ".inpcrd",
        ".parm7" : ".prmtop"
    }

    # checking if the charmm_file exists
    if not os.path.exists(charmm_file):
        raise FileNotFoundError("CHARMM-GUI file does not exists")

    print('creating folders')
    os.mkdir(out_amber_dir)
    amber_dir = os.path.abspath(out_amber_dir)
    # Goes into the CHARMM-gui folder and then into amber folder and obtains the .pdb .rst7 and
    print("Extracting and formating files for AMBER simulations")
    for path, dir, files in os.walk(charmm_dir):
        if path.endswith("amber"):
            os.chdir(path)
            if os.path.exists('step5_charmm2amber.complete.pdb'):
                print('DETECTED: CHARMM-GUI outputs contains AMBER force fields')
                charmm_files = ["step5_charmm2amber.complete.pdb", "step5_charmm2amber.rst7", "step5_charmm2amber.parm7"]
                for charm_file in charmm_files:
                    shutil.copy(charm_file, amber_dir)
            else:
                print('DETECTED: CHARMM-GUI outputs contains CHARMM or CHARMM36m force fields')
                charmm_files = ["step5_input.pdb", "step5_input.rst7", "step5_input.parm7"]
                for charm_file in charmm_files:
                    shutil.copy(charm_file, amber_dir)

    # checks if the script is in the amber folder
    if os.getcwd() == cwd:
        raise FileNotFoundError("The 'amber' directory was not found within the extracted CHARMM-GUI folder")

    os.chdir(amber_dir)

    # renaming files to the appropiate extensions
    amber_files = glob.glob("*")
    if len(amber_files) != 3:
        raise ValueError("Incorrect number of files were extracted from the CHARMM-GUI folder. ")

    for file in amber_files:
        _, ext = os.path.splitext(file)
        name = file.replace(file, "{}_md{}".format(sysname, ext_trans[ext]))
        os.rename(file, name)
    os.chdir(cwd)


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


if __name__ == "__main__":

    # help options
    if len(sys.argv) == 1:
        help_message()

    elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
        help_message()

    elif sys.argv[1] == '--version' or sys.argv[1] == '-v':
        print('charmm2amber {}'.format(__version__))
        sys.exit()

    # CLI arguments
    parser = argparse.ArgumentParser(add_help=False)
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-i', '--input', type=str, required=True)
    required.add_argument('-s', '--sysname', type=str, required=True)
    optional.add_argument('-r', '--sysres', type=int, required=False, default=None)
    optional.add_argument('-o', '--overwrite', default=False, action='store_true', required=False)
    #optional.add_argument('-t', '--tpye', type=str,default="membrane", choices=["membrane", "solvated"], required=False)
    args = parser.parse_args()

    # checking if any files charmm or amber files exists
    wdir = os.getcwd()
    comp_file = "{}_CHARMM-GUI.tgz".format(args.sysname)
    pdb_file = "{}_md.pdb".format(args.sysname)
    prmtop_file = "{}_md.prmtop".format(args.sysname)
    rst_file = "{}_md.rst".format(args.sysname)
    charmm_dir_name = "{}_CHARMM-GUI".format(args.sysname)
    amber_dir_name = "{}_AMBER".format(args.sysname)


    # checking if the directories are true
    if os.path.exists(charmm_dir_name) and args.overwrite == False:
        raise FileExistsError('The directory {} already exists. Please execute this porgram in a new directory or use the "-o" options to overwrite the existing files'.format(charmm_dir_name))
    elif os.path.exists(charmm_dir_name) and args.overwrite:
        print('WARNING: Overwriting previous CHARMM-GUI directories...')
        reset(wdir, args.sysname)

    if os.path.exists(amber_dir_name) and args.overwrite == False:
        raise FileExistsError('The directory {} already exists. Please execute this program in a new diretiory or use -o to overwrite the existing directory'.format(amber_dir_name))
    elif os.path.exists(amber_dir_name) and args.overwrite:
        print('WARNING: Overwriting previous AMBER directories...')
        rm_cmd = "rm -f {}".format(amber_dir_name)
        subprocess.run(rm_cmd, shell=True)

    # extracting files
    print("Extracting data")
    charmm_file = decompress_charmmfile(args.input, charmm_dir_name)

    # extrat files from charmm_gui file
    extract_and_format(charmm_dir_name, args.sysname, amber_dir_name)
    # going to the amber directory and prepair for simulations
    os.chdir(amber_dir_name)
    res_check = res_count(pdb_file)  # returns {int} --> number of resudes of system
    if args.sysres is None or args.sysres == res_check:  # default is set to none in order to use res_check value
        print("Preparing inputs files for AMBER simulation")
        amber_cmd = 'amber_run_setup.pl -s {} -r {}'.format(args.sysname, res_check).split()
        subprocess.run(amber_cmd, shell=True)

        clean_up(wdir, comp_file, amber_dir_name, charmm_dir_name)

        print("Charmm2amber is complete!")

    elif res_check != args.sysres:  # use elif res_check == rescheck is false --> use int
        print('MESSAGE: Resiude check: FAILED')
        print('WARNING: The amount of residues specified does not match with the total amount of CA atoms obtained from the pdb file.')
        print('This is the correct amount: {}'.format(res_check))

        # user reponse to custome resiude count
        response_count = 0
        while True:
            usr_res_response = input('\nDo you still wish to use {} as your residue count? (Y/n): '.format(args.sysres))

            # If the response is yes, amber files will be generated
            if usr_res_response.lower() == 'yes' or usr_res_response.lower() == 'y':
                print('MESSAGE: Using {} reisudes count to build your simulation ...'.format(res_check))
                amber_cmd = ' amber_run_setup.pl -s {} -r {}'.format(args.sysname, res_check)
                subprocess.run(amber_cmd, shell=True)

                clean_up(wdir, comp_file, amber_dir_name, charmm_dir_name)

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
                        reset(wdir, args.sysname)
                        exit()

                    # asking the user if the they want to use the default residue count
                    default_response = input(f'\nWill you like to use the default number of residues of your system? (Y/n): ')

                    # if the response is yes, create the amber files
                    if default_response.lower() == 'y' or default_response.lower() == 'yes':
                        print('Using {} residues to buld your simulation files'.format(res_check))
                        amber_cmd = ' amber_run_setup.pl -s {} -r {}'.format(args.sysname, res_check)
                        subprocess.run(amber_cmd, shell=True)
                        clean_up(wdir, comp_file, amber_dir_name, charmm_dir_name)
                        print("Charmm2amber is complete!")
                        exit()

                    # if the response is no, ask for a new input
                    elif default_response.lower() == 'n' or default_response.lower() == 'n':
                        new_count_attempts = 0
                        while True:
                            try:
                                # attempt checker
                                if new_count_attempts == 3:
                                    print('Too many failed attempts. Exiting program.')
                                    reset(wdir, args.sysname)
                                    exit()

                                # user inputs new res count. Does not save value if the new value is bigger than res_check's
                                new_count = int(input('Please enter your new reisude count: '))
                                if new_count > res_check:
                                    print('WARNNING: The number of resiudes provided exceeds the total amount of reisudes that your system has! \nYour system has {} residues!'.format(res_check))

                                else:
                                    print('using {} resiudues to build your simulation files.'.format(new_count))
                                    amber_cmd = 'amber_run_setup.pl -s {} -r {}'.format(args.sysname, new_count).split()
                                    subprocess.run(amber_cmd)
                                    clean_up(wdir, comp_file, amber_dir_name, charmm_dir_name)
                                    print("Charmm2amber is complete!")
                                    exit()

                            except ValueError:
                                print('ERROR: The input you have provided is not an integer. Please enter an integer.')
                                new_count_attempts += 1
                    else:
                        print('MESSAGE: Please enter a valid response')
                        default_attempts += 1


            # 3 fail attempts causes the program to reset and exit
            elif response_count == 3:
                print('MESSAGE: Too many failed attempts. Exiting program.')
                reset(wdir, args.sysname)
                exit()

            else:
                print('Invalid response. Please try again.')
                response_count += 1
    else:
        print('Uh oh something went wrong!')
        exit()
