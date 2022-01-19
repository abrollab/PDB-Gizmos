# NOTE: custom classes to be called when using argparser 
import argparse


class ParseSelection(argparse.Action):
        """ converts the use specfied selection to the appropiate format for rmsd calculations with selected atoms"""
        def __call__(self, parser, namespace, string, atom_type="CA"):
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