# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import argparse
import xml.etree.ElementTree as ET

import requests


def get_tm_regions(pdbtm_xml):
    root = ET.fromstring(pdbtm_xml)
    tmregions_data = []
    for elm in root.find("."):
        tag = elm.tag.split("}")[-1]
        if tag == "CHAIN":
            for chain_elm in elm:
                region_tag = chain_elm.tag.split("}")[-1]
                if region_tag == "REGION":
                    data = chain_elm.attrib
                    helix_check = data["type"]
                    if helix_check == "H":
                        row_data = "{},{},{}".format(data["pdb_beg"], data["pdb_end"], int(data["pdb_end"]) - int(data["pdb_beg"])  + 1)
                        tmregions_data.append(row_data)
    return tmregions_data

if __name__ == "__main__":
    
    # cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="pdbid", metavar="PDBID" )
    args = parser.parse_args()
    pdbtm_api = "http://pdbtm.enzim.hu/data/database/{}/{}.xml".format(args.input[1:3], args.input.lower())

    print(pdbtm_api)
    r = requests.get(pdbtm_api)
    if r.status_code != 200:
        raise ConnectionAbortedError("Invalid pdbid has been give, or there is no internet connection")
    xml = r.text
    data = get_tm_regions(xml)
    
    cols = "tm_beg, tm_end, tm_length" 
    print(args.input)
    print(cols)
    outfile_name = "{}_tm_lengths.csv".format(args.input)
    with open(outfile_name, "w") as csv:
        csv.write("{},,\n".format(args.input))
        csv.write("{}\n".format(cols))
        for line in data:
            print(line)
            csv.write("{}\n".format(line))

    print("{} has been saved to your directory".format(outfile_name))
