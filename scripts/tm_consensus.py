#!/home/exec/anaconda3/bin/python
import os
import sys
import argparse
import requests
from textwrap import dedent
from time import sleep
from collections import defaultdict
from bs4 import BeautifulSoup

__version__ = "0.1.0"

# External requests
def get_pdbtm_xml(pdbid, buffer=1):
    """ Connects to pdbTM database and return xml file"""
    if len(pdbid) != 4:
        raise ValueError("Incorrect pdbid was porvided")
    pdb_tag = pdbid[1:3]
    pdbtm_url = "http://pdbtm.enzim.hu/data/database/{}/{}.xml".format(pdb_tag, pdbid)
    xml = requests.get(pdbtm_url).content
    sleep(buffer) # Time buffer to prevent spam requesting for servers
    return xml


# main functions used
def parse_pdbtm_xml(pdbtm_xml):
    """ Parses xml contents and obtains the TM regions of the structure """

    # initating parser
    soup = BeautifulSoup(pdbtm_xml, "lxml")

    # extacting receptor chain and tm regions H = TM helix in pdbTM
    tm_regions = soup.find_all("region", attrs={"type" : "H"})
    if len(tm_regions) != 7:
        raise RuntimeError("This protein structure does not have 7 helices")

    # obtaining lables of each tm region
    labled_tms = defaultdict(None)
    for idx, tm_region in enumerate(tm_regions):
        attributes = tm_region.attrs
        tm_name = "tm{}".format(idx+1)
        beg = attributes["pdb_beg"]
        end = attributes["pdb_end"]
        labled_tms[tm_name] = (beg, end)
    return labled_tms


def get_consensus(array_of_labled_tms):
    """ takes in an array of labled tms and find the consensus tm range """

    # Prepairing data
    labled_tm_ranges = defaultdict(list)
    for labled_pairs in array_of_labled_tms.values():

        tm1_range_tup = tuple([int(vals) for vals in labled_pairs["tm1"]])
        tm1_resids = [i for i in range(tm1_range_tup[0], tm1_range_tup[-1])]
        labled_tm_ranges["tm1"].append(tm1_resids)

        tm2_range_tup = tuple([int(vals) for vals in labled_pairs["tm2"]])
        tm2_resids = [i for i in range(tm2_range_tup[0], tm2_range_tup[-1])]
        labled_tm_ranges["tm2"].append(tm2_resids)

        tm3_range_tup = tuple([int(vals) for vals in labled_pairs["tm3"]])
        tm3_resids = [i for i in range(tm3_range_tup[0], tm3_range_tup[-1])]
        labled_tm_ranges["tm3"].append(tm3_resids)

        tm4_range_tup = tuple([int(vals) for vals in labled_pairs["tm4"]])
        tm4_resids = [i for i in range(tm4_range_tup[0], tm4_range_tup[-1])]
        labled_tm_ranges["tm4"].append(tm4_resids)

        tm5_range_tup = tuple([int(vals) for vals in labled_pairs["tm5"]])
        tm5_resids = [i for i in range(tm5_range_tup[0], tm5_range_tup[-1])]
        labled_tm_ranges["tm5"].append(tm5_resids)

        tm6_range_tup = tuple([int(vals) for vals in labled_pairs["tm6"]])
        tm6_resids = [i for i in range(tm6_range_tup[0], tm6_range_tup[-1])]
        labled_tm_ranges["tm6"].append(tm6_resids)

        tm7_range_tup = tuple([int(vals) for vals in labled_pairs["tm7"]])
        tm7_resids = [i for i in range(tm7_range_tup[0], tm7_range_tup[-1])]
        labled_tm_ranges["tm7"].append(tm7_resids)

    # TODO: figure out how to get the consensues
    consensus_range_per_tm = defaultdict(None)
    for tm, tup_range_list in labled_tm_ranges.items():
        overlapping_resids = sorted(tuple(set(tup_range_list[0]).intersection(*tup_range_list)))
        if len(overlapping_resids) == 0:
            # when there is an outlier, the length of the set will be 0
            # -- for now an error will rise, later a function will take care of it
            # TODO: create "remove_outlier()" function
            raise ValueError("Outlier has been found in the data. Removing remove_outlier() method under development")
        consensus_tmrange = overlapping_resids[0], overlapping_resids[-1]
        consensus_range_per_tm[tm] = consensus_tmrange
    return consensus_range_per_tm


def help_message():
    """ displays help message """
    message = dedent("""
    tm_consensus.py
    version: {}
    Finds tm consensus range from multiple pdbids

    USE CASE EXAMPLE:
    -----------------
    tm_consensus.py -i 3sn6 2rh1 # adding multiple pdb ids

    ARGUMENTS:
    ----------
    -i, --input      pdb id(s)
                     """.format(__version__))

if __name__ == "__main__":
 # Help message
    if len(sys.argv) == 1:
        help_message()
    elif sys.argv[1] == "-h" or sys.argv[1].lower() == "--help":
        help_message()
    # CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs="+", required=True)
    args = parser.parse_args()

    labled_tms_allpdbs = defaultdict(None) # data
    for pdbid in args.input:
        contents = get_pdbtm_xml(pdbid)
        tm_ranges = parse_pdbtm_xml(contents)
        labled_tms_allpdbs[pdbid] = tm_ranges

    consensus = get_consensus(labled_tms_allpdbs)
    print("Here are the results")
    for tm, tm_range in consensus.items():
        beg, end = tm_range
        print("{}: {} to {}".format(tm, beg, end))
