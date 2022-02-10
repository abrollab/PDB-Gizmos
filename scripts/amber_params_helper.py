#!/home/exec/anaconda3/bin/python
import sys
import os
import argparse
from textwrap import dedent
from collections import defaultdict
from tabulate import tabulate
from bs4 import BeautifulSoup

def parse_and_extract(html_file):
    """Parses HTML table contents and extracts AMBER paramters

    Parameters
    ----------
    contents : str
        Contents of HTML table

    Returns
    -------
    list
        list of list containing parameter and description

    """
    contents = open(html_file).read()
    soup = BeautifulSoup(contents, features="html.parser")
    table_rows = soup.find_all("tr")

    amber_params = []
    amber_params.append(["parameter", "description"])
    for row in table_rows:
        table_data = row.find_all("td")
        param = table_data[0].text.replace("\n", "")
        description_list = table_data[1].text.replace("\n", "").split()

        # formating lines removing long strings
        # -- chunking them into 15 words
        description_chunks = [(" ".join(description_list[i:i+15])) for i in range(0, len(description_list), 15)]
        description = "\n".join(description_chunks)
        results = [param, description]
        amber_params.append(results)

    return amber_params


def convert_to_dict(content_list):
    """Converts list of contents int a dictionary

    Parameters
    ----------
    content_list : list
        list of extracted contents

    Returns
    -------
    dict
        contains parameters and description as key-value pairs
    """
    amber18_params_dict = defaultdict(lambda: None)
    for param, desc in content_list:
        amber18_params_dict[param] = desc
    return amber18_params_dict

def help_message():
    msg = dedent("""
    amber_params.py simple program that shows the documentation of
    amber parameters.

    USAGE:
    1. python amber_params.py              # Display all parameters and description
    2. python amber_params.py -s ntwv ntt  # Displays specific parameters and description

    HELP:
    python amber_params.py -h
    python amber_params.py --help

    PARAMETERS:
    -s, --search        If not flagged, all paramters and descriptions are shown. For searching
                        specific paramters, flag the "-s" argument and add amber specific amber
                        paramters (look at USAGE #2). If the user provides a parameter that does
                        not exists, "N/A" will be returned under the description column

    Current Amber18 input paramters:
    --------------------------------
    ['parameter', 'barostat', 'cut', 'dt', 'gamma_ln', 'ibelly', 'ig', 'imin', 'ioutfm', 'irest',
    'iwrap', 'maxcyc', 'ncyc', 'nmropt', 'nsnb', 'nstlim', 'ntb', 'ntc', 'ntf', 'ntp', 'ntpr',
    'ntr', 'ntt', 'ntwv', 'ntwx', 'ntx', 'pres0', 'restraint_wt', 'restraintmask', 't', 'taup',
    'tautp', 'temp0', 'tempi', 'vlimit']
    """)
    print(msg)
    exit()

if __name__ == "__main__":

    # Help message
    # -- used try except block to allow USAGE #1
    try:
        if sys.argv[0] == '-h' or sys.argv[0] == '--help':
            help_message()
        elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
            help_message()
    except:
        pass

    # CLI arguments
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-s", "--search", nargs="+", default=None)
    args = parser.parse_args()

    # load in file
    # html_file = "./data/amber18_params.html"
    script_dir = os.path.abspath(__file__).rsplit("/", 1)[0]

    html_file = os.path.join(script_dir, "data/amber18_params.html")
    if not os.path.exists(html_file):
        raise RuntimeError("Unable to find parsable contents")

    # parsing html contens and extact parameters and description
    contents = parse_and_extract(html_file)


    # checking if the user wanted specific definition or all
    if args.search is None:
        print(tabulate(contents, headers="firstrow",
                       tablefmt="fancy_grid"))
    else:
        # convert list into dictionary
        param_dict = convert_to_dict(contents)

        selected_params = []
        selected_params.append(["parameter", "description"])

        for query in args.search:
            description = param_dict[query]
            if description is None:
                result = [query, "N/A"]
                selected_params.append(result)
            else:
                result = [query, description]
                selected_params.append(result)

        print(tabulate(selected_params, headers="firstrow",
                       tablefmt="fancy_grid"))
    sys.exit("Process complete!")