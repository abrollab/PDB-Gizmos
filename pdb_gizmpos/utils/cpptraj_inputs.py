# NOTE: it is wrapper that writes out cpptraj infiles for trajectory processing.

import mdtraj as md


class CpptrajWrapper:

    def __init__(self, name, topology, traj, stride=1):
        self.name = open(name, "w")
        self.topology = topology
        self.traj = traj


    def preprocess(self, autoimg_idx=(), strip_idx=()):
        """ Creates default paramters for autoimaging and striping """

        # checking inputs
        if not isinstance(autoimg_idx, tuple):
            raise TypeError("Provided values for autoimg_idx are not in tuple format, you have provided {}".format(type(autoimg_idx)))
        elif len(autoimg_idx) != 2:
            raise ValueError("You have provided the incorrect amount of values. Only requires 2. You have provided".format(len(autoimg_idx)))

        if not isinstance(strip_idx, tuple):
            raise TypeError("Provided values for strip_idx are not in tuple format, you have provided {}".format(type(strip_idx)))
        elif len(strip_idx) != 2:
            raise ValueError("You have provided the incorrect amount of values. Only requires 2. You have provided".format(len(strip_idx)))

        # writing the input file
        self.topology.write("parm {}".format(self.topology))
        self.topology.write("trajin {}".format(self.traj))
        self.topology.write("autoimage")
        self.topology.write("strip !:{}-{} outprefix strip".format(strip_idx[0], strip_idx[1]))
        self.topology.write("trajout strp_{}".format(self.traj))
        self.topology.write("run")

    def add_custom_params(self, paramters):
        """ Create your own cpptraj.in file """
        self.name.write(paramters)

    def describe(self):
        """ prints out what is currently written in the file """
        pass



