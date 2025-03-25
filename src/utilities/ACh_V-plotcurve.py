#import opencor as oc
import sys
import numpy as np
from opencor_helper import SimulationHelper
import csv
#from PyQt5.QtWidgets import QApplication
import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import paperPlotSetup
matplotlib.use('Agg')

# TODO 
#preset some address, such as input model address, results saved address
file_path = "/home/cdon822/Documents/OpenCOR/NEs_to_SAN.cellml"
Outputfile_address = "/home/cdon822/Documents/GIT_files/my_project/simulation results/SAN_model"
#create a new temporary files to save the results
save_newfilename1 = "ACh-V"
#spliced into new address
save_addr01 = Outputfile_address + "/"+save_newfilename1+"/Iso_0_V_plot.png"
save_addr02 = Outputfile_address + "/"+save_newfilename1+"/Iso_0_I_plot.png"

str_title = "100nM ACh"

#those are parameters that need to test in this scripts
#exp:[Membrane/V_node] represent the [module/variable_name]

#obs_list = ['Rate_modulation_experiments/q_I','Rate_modulation_experiments/q_b1GsI']
#str_title = "ISO-beta1AR relationship"
#obs_list = ['Rate_modulation_experiments/q_I','Rate_modulation_experiments/q_b2GsI']
#str_title = "ISO-beta2AR relationship"
#obs_list = ['Rate_modulation_experiments/q_I','Rate_modulation_experiments/q_Gs']
#str_title = "ISO-Gs relationship"
#obs_list = ['Rate_modulation_experiments/q_I','Rate_modulation_experiments/q_Gi']
#str_title = "ISO-Gi relationship"
#obs_list = ['Rate_modulation_experiments/q_I','Rate_modulation_experiments/q_ACGs']
#str_title = "ISO-ACGs relationship"
obs_list = ['Rate_modulation_experiments/ACh','Membrane/V']
#str_title = "ISO-cAMP relationship"


#save the results about Iso=0, V-T and I-T curve
#preset the fontsize for specific parameters, only need set once
plt.rcParams['axes.labelsize'] = 24
plt.rcParams['xtick.labelsize'] = 24
plt.rcParams['ytick.labelsize'] = 24
plt.rcParams['axes.titlesize'] = 24

#I don't know why cannot show the curve, but can save the curve
#app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()

#which parameter need to extract and reset the value during iteration
#type: ['function_name/variable_name']
reset_param_names = ['Rate_modulation_experiments/ACh']
#set initial value
reset_param_val = [100.0]
#define a variable that save result from iteration
inputs = np.arange(0,2.2001,0.0001)


x = SimulationHelper(file_path, 0.0001, 2.2, pre_time=0)
#used for debug
#print("ii=",ii)
x.set_param_vals(reset_param_names, reset_param_val)
x.run()
z = x.get_results(obs_list)
z1 = z[1][0]
#z_out = z[1][100]
#print the output

outputs = z1.copy()
print("outputs=",outputs.shape)
print("inputs=",inputs.shape)

x.close_simulation()

#set the final curve saved address and image name
save_addr1 = Outputfile_address + "/"+save_newfilename1+"/ACh_100nM2.png"
plt.plot(inputs,outputs,marker='.',linestyle='-',color='b',label='curve-relationship')
plt.title(str_title)

plt.xlabel('t [s]')
plt.ylabel('V [mV]')
plt.grid(False)
plt.savefig(save_addr1,bbox_inches='tight')
plt.clf()
print("results saved as 'png' type")
#print("[in,out]=",inputs, outputs)

# I don't know why cannot plot the result curve, but can save it in the script address
#plt.show()



