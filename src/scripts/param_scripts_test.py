'''
Created on 29/10/2021

@author: Finbar J. Argus
'''

import opencor as oc
import sys
import os
import pandas as pd
from mpi4py import MPI
from distutils import util, dir_util


root_dir = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(os.path.join(root_dir, 'src'))

user_inputs_dir = os.path.join(root_dir, 'user_run_files')

from param_id.paramID import CVS0DParamID
import traceback
import yaml

if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    try:
        run_param_id()
        MPI.Finalize()
    except:
        print(traceback.format_exc())
        comm.Abort()
        exit()
