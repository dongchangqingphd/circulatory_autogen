#import opencor as oc
import sys
import numpy as np
import pandas as pd
from opencor_helper import SimulationHelper
from scipy.signal import find_peaks
import csv
#from PyQt5.QtWidgets import QApplication
import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import paperPlotSetup
matplotlib.use('Agg')



def compute_peak_period(timeline,V_data):
    #got data and timeline
    timet = timeline
    voltage = V_data
    
    # 仅保留第5秒之后的数据
    mask = timet >= 5.0
    time = timet[mask]
    signal = voltage[mask]
    
    # 寻找最大峰值和最小峰值
    peaks_max, _ = find_peaks(signal)
    peaks_min, _ = find_peaks(-signal)  # 负信号寻找最小峰值
    
    peak_times_max = time[peaks_max]
    peak_values_max = signal[peaks_max]
    peak_times_min = time[peaks_min]
    peak_values_min = signal[peaks_min]
    
    mean_maxV = np.mean(peak_values_max)
    mean_minV = np.mean(peak_values_min)
    #print("maxV=",mean_maxV)
    #print("minV=",mean_minV)
    
    # 计算相邻峰值之间的时间间隔（周期）
    if len(peak_times_max) > 1:
        periods = np.diff(peak_times_max)
        avg_period = np.mean(periods)
    else:
        avg_period = np.nan  # 如果找不到足够的峰值
    
    peak_freq = 1.0/avg_period
    
    # 计算每个周期内的平均值
    avg_values_per_period = []
    for i in range(len(peak_times_max) - 1):
        mask_period = (time >= peak_times_max[i]) & (time < peak_times_max[i + 1])
        avg_values_per_period.append(np.mean(signal[mask_period]))
    
    mean_avgV = np.mean(avg_values_per_period)
    #print("meanV=",mean_avgV)
    
    #another way to calculate period
    peak_idxs, peak_properties = find_peaks(signal)
    if len(peak_idxs) < 2:
        # there aren't enough peaks to calculate a period
        # so set the period to the max time of the simulation
        period2 = time[-1] - time[0]
    else:
        # calculate the average period between peaks
        period2 = np.sum([time[peak_idxs[II+1]] - time[peak_idxs[II]] for II in range(len(peak_idxs)-1)])/(len(peak_idxs) - 1)
        
    startv = peak_idxs[0]
    endv = peak_idxs[len(peak_idxs)-1]
    V_period = signal[startv:endv]
    
    V_mean = np.mean(V_period)
    #print("V_mean=",V_mean)
    
    
    
    print("calculated frequency:",peak_freq)
    #print(f"Estimated Period from Peaks: {avg_period:.12f} s")
    #print(f"Max Peaks: {peak_values_max}")
    #print(f"Min Peaks: {peak_values_min}")
    #print(f"Average Values per Period: {avg_values_per_period}")
    

    return peak_freq



# TODO 
#preset some address, such as input model address, results saved address
file_path = "/home/cdon822/Documents/GIT_files/circulatory_autogen/generated_models/SANHR11/SANHR11.cellml"
Outputfile_address = "/home/cdon822/Documents/GIT_files/my_project/simulation results/SAN_model"
#create a new temporary files to save the results
save_newfilename1 = "fit rabbit SANC"
#spliced into new address
save_addr01 = Outputfile_address + "/"+save_newfilename1+"/Iso_0_V_plot.png"
save_addr02 = Outputfile_address + "/"+save_newfilename1+"/Iso_0_I_plot.png"

str_title = "CCh-HR relationship"

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
obs_list = ['NES/ISO','hrv/V']
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
reset_param_names = ['NES/ACh_init','NES/ISO_init']
#set initial value
reset_param_val = [0.01,1]
simulation_time = 10
simulation_dt = 0.0001
max_time = simulation_time + simulation_dt
#define a variable that save result from iteration
inputs = np.arange(0,max_time,simulation_dt)

#define a variable that save result from iteration
NEs = []
HRf = []
for ii in range(1,64):
    #x = SimulationHelper(file_path, 0.01, 10, maximumNumberofSteps=1000, maximum_step=0.001, pre_time=0)
    #used for debug
    print("ii=",ii)
    x = SimulationHelper(file_path, simulation_dt, simulation_time, pre_time=0)
    reset_param_val[0] = reset_param_val[0]*1.2
    x.set_param_vals(reset_param_names, reset_param_val)
    x.run()
    z = x.get_results(obs_list)
    z1 = z[1][0]
    #z_out = z[1][100]
    #print the output

    outputs = z1.copy()
    print("ACh=",reset_param_val[0])
    frequency_HR = compute_peak_period(inputs,outputs)
    NEs.append(reset_param_val[0])
    HRf.append(frequency_HR)
#print("inputs=",inputs.shape)

x.close_simulation()


reset_param_val2 = [0,1]
x_rst = SimulationHelper(file_path, simulation_dt, simulation_time, pre_time=0)
x_rst.set_param_vals(reset_param_names, reset_param_val2)
x_rst.run()
z_rst = x_rst.get_results(obs_list)
z1_rst = z_rst[1][0]
outputs_rst = z1_rst.copy()
frequency_HR_std = compute_peak_period(inputs,outputs_rst)
print("frequency_Std=",frequency_HR_std)
print("HRf=",HRf)
#HRf = 100.0*HRf/frequency_HR_std
HRf2 = [x*100.0/frequency_HR_std for x in HRf]


#set the final curve saved address and image name
save_addr1 = Outputfile_address + "/"+save_newfilename1+"/CCh_HR-curve.png"
plt.plot(NEs,HRf2,marker='.',linestyle='-',color='b',label='curve-relationship')
plt.title(str_title)
plt.xscale('log')
plt.xticks([0.1, 1, 10, 100, 1000], labels=["0.1", "1", "10", "100", "1000"])



#add error bar in curve
x1 = [0,100,500,1000]
y1 = [100,73,45,29]
yerr = [10,10.5,15,11]
y_err = [y1[x1.index(val)] for val in x1]
yerr_err = [yerr[x1.index(val)] for val in x1]

#plot error bar in curve
plt.plot(x1,y1,marker='x', linestyle='None')
plt.errorbar(x1,y_err,yerr=yerr_err,fmt='x', capsize=5,color='red',label='experimental data')



plt.xlabel('CCh concentration [nM]')
plt.ylabel('HR frequency [Hz]')
plt.grid(False)
plt.savefig(save_addr1,bbox_inches='tight')
plt.clf()
print("finish scripts")
#print("[in,out]=",inputs, outputs)

# I don't know why cannot plot the result curve, but can save it in the script address
#plt.show()



