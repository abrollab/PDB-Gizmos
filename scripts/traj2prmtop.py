#!/home/exec/anaconda3/bin/python
# traj2prmtop is a simple cpptraj wrapper that converts selected frames from a s
# tajectory and converts it into a amber .prmtop file
# Lab: Abrol Lab
# Dev: Erik Serrano
# Email: erik.serrano.318@my.csun.edu

import os
import sys
import argparse
import subprocess
import shutil
import warnings
from textwrap import dedent


def infile_writer(prmtop_path, traj_path, frame, outname="prmtop_out"):
	""" Writes a cpptraj input file that converts a selelcted

	Arguments:
	---------
	prmtop_path : str
		Path to prmtop file
	traj_path : str
		Path to .nc file
	frame : str
		Index selection of frame of intrest
	outname : str, optional
		Name of generated .prmtop file (default = 'prmtop_out')

	Returns
	-------
	str
		Path to cpptraj infile
	"""
	infile_name = "cpptraj_traj2prmtop.in"
	with open(infile_name, "w") as cpptraj_file:
		cpptraj_file.write("parm {}\n".format(prmtop_path))
		cpptraj_file.write("trajin {} {}\n".format(traj_path, frame))
		cpptraj_file.write("parmwrite out {}.prmtop\n".format(outname))
		cpptraj_file.write("go\n")
		cpptraj_file.write("exit\n")

	infile_path = os.path.abspath(infile_name)
	return infile_path

def stdout_err(err_msg):
	""" Parses cpptraj error message to make it readable
	Arguments:
	err_msg : str
		Error message from cpptraj
	"""

	print("-"*10,"Error message","-"*10)
	msg = err_msg.split("\n")
	for line in msg:
		print(line)


def cpptraj_executor(infile):
	""" executes cpptraj with given input file

	Arguments:
	---------
	infile : str
		Path to cpptraj infile
	"""

	# checking if cpptraj is installed
	check = shutil.which("cpptraj")
	if check is None:
		raise RuntimeError("Unable to find cpptraj executable")

	# executing cpptraj
	# -- command must be split because subprocess.run takes in a list of commands
	cpptraj_cmd = "cpptraj -i {}".format(infile).split()
	proc = subprocess.run(cpptraj_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if proc.returncode != 0:
		print("ERROR: Cpptraj Encounter and errror.")
		stdout_err(proc.stderr.decode("utf-8"))
		sys.exit(1)


def help_message():
	"""custome help message"""
	print(dedent("""
	traj2prmtop.py is a simple cpptraj wrapper that allows converting a single frame
	from a trajectory and converts it into an AMBER .prmtop file.

	NOTE:
	-----
	This program supports VMD indexing. VMD indexing is converted into a cpptraj
	indexing internally.

	USAGE
	-----
	# Example1: getting single frame with index
	python traj2prmtop.py -p yourfile.prmtop -x your_traj.nc -f 34

	# Example 2: using cpptraj unique selection i.e 'lastframe'
	python traj2prmtop.py -p yourfile.prmtop -x your_traj.nc -f lastframe

	# Example 3: using Help message (3 ways)
	python traj2prmtop.py
	python traj2prmtop.py -h
	python traj2prmtop.py --help

	Arguments
	---------
	-p, --prmtop       Path to .prmtop topology file
	-x, --traj         Path to .nc trajectory file
	-f, --frame        Frame index of intrest

	Optional:
	---------
	-o, --outname      Name of generated .prmtop file (default)
	"""))

if __name__ == "__main__":

	# help message encounters
	if len(sys.argv) == 0 or len(sys.argv) == 1:
		help_message()
	elif sys.argv[1] == "-h" or sys.argv[1].lower() == "--help":
		help_message()
	elif sys.argv[2] == "-h" or sys.argv[2].lower() == "--help":
		help_message()

	# CLI commands
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("-p", "--prmtop", type=str, required=True)
	parser.add_argument("-x", "--traj", type=str, required=True)
	parser.add_argument("-f", "--frame", type=str, required=True)
	parser.add_argument("-o", "--outname", default="prmtop_out", type=str, required=True)
	args = parser.parse_args()

	# converting into cpptraj indexting (cpptraj indexing starts at 1)
	check = str(args.frame).isdigit()
	accepted_inputs = ["lastframe", "-1"]
	if check is True:
		args.frame = str(int(args.frame) + 1)
	elif not str(args.frame) in accepted_inputs:
		raise ValueError("{} is not an acceptable index selection for cpptraj or it is not supported".format(args.frame))

	# outname checking
	if "." in str(args.outname):
		warn_msg = "Warning, extensions are not required to be explicitly defined. Removing..."
		warnings.warn(warn_msg, SyntaxWarning)
		args.name = "_".join(args.outname.rsplit(".",-1)[:-1])

	# writing cpptraj file
	infile = infile_writer(args.prmtop, args.traj, args.frame, args.outname)

	# executing
	cpptraj_executor(infile)
