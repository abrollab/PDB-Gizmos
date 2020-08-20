# TODO:  rename the log file if the name already exists 
###############################################################################

################################################################################
# logger.py 
# Is a user defined class that allows to tracked the output of the program
# Logging will be supported in to all scripts within the pdbTools package 
# Light weight logging system for
# Allows the user to find errors within the program with ease 
################################################################################
import textwrap
from pathlib import Path


class Logger:
    """ Creates a logger file that will be used to stored all of the debugg
    information that occurs in runtime
    """
    def __init__ (self, log_file):
        self.log_file = open(log_file, 'w+')

    def log_new_stage(self, message):
        """ Writes a seperation when running outputs from a new stage"""
        sep_message = textwrap.dedent("""\n
        {} 
        {}    
        {}\n
        """.format('#'*len(message), message, '#'*len(message)))
        self.log_file.write(sep_message)

    def log_warning(self, w_message):
        """ Writes message with a 'WARNING' tag"""
        self.log_file.write('WARNING: {}\n'.format(w_message))

    def log_message(self, message ):
        """ Writes a message long in the log"""
        self.log_file.write('MESSAGE: {}\n'.format(message)) 
        
    def log_error(self, e_message):
        """ Writes a message with an ERROR tag and explains why the runtime failed"""
        self.log_file.write('ERROR: {}\n'.format(e_message))

    def close_log(self, c_message=None):
        """Closes the logger file"""
        if c_message is None: 
            self.log_file.close()
        else:
            self.log_file.write('CLOSING: {}. \n '.format(c_message))
            self.log_file.close()

