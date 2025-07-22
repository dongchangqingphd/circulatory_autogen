import sys
import numpy as np
from opencor_helper import SimulationHelper
import subprocess
import csv
import re
import os
import json
from scipy.fft import fft, fftfreq
from scipy.fft import rfft, rfftfreq
from scipy.signal import find_peaks
from decimal import Decimal
#import pandas as pd

np.set_printoptions(precision=20)

#this script used for automatic find the boundary condition values (up and down)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

#not correct detect period, for example: [34,12]
def analyze_signal_from_data(time, voltage):
    # 4. Calculate average period using FFT
    N = len(voltage)
    if N < 2:
        raise ValueError("Not enough data after the specified start_time.")
    
    sampling_interval = time[1] - time[0]  # Sampling interval (assumed uniform)
    sampling_rate = 1 / sampling_interval
    #print("[debug]T=",sampling_interval)
    
    yf = rfft(voltage)
    xf = rfftfreq(N, sampling_interval)
    
    # Skip DC component, find dominant frequency
    amplitude = np.abs(yf)
    peaks, _ = find_peaks(amplitude[1:], height=0.05 * np.max(amplitude))  
    peaks += 1  
    #print("[debug]peaks=", peaks)
    #print("[debug]xf=", xf)
    peak_idx = peaks[0]
    num_peak = peak_idx
    dominant_freq = xf[peak_idx]
    average_period = 1.0 / dominant_freq
    #print("[debug]dominant_freq=", average_period)
    min_distance_samples = int(0.8 * average_period / sampling_interval)  
    peaks_indices, _ = find_peaks(voltage, distance=min_distance_samples)
    selected_peaks = peaks_indices[:peak_idx]
    peak_APv = voltage[selected_peaks]
    #print("[debug]peaks_indices=", peaks_indices)
    #print("[debug]peaks=", peaks)
    #print("[debug]num_peak=", num_peak)
    #print("[debug]selected_peaks=", selected_peaks)
    first_pos = time[selected_peaks[0]]
    last_pos = time[selected_peaks[-1]]
    mean_period = (last_pos-first_pos)/(num_peak-1)
    #print("[debug]mean_period=", mean_period)
    
    mean_maxV = np.mean(peak_APv)
    #print("[debug]mean_maxV=", mean_maxV)
    
    negative_peaks_indices, _ = find_peaks(-voltage, distance=min_distance_samples)
    #print("[debug]negative_peaks_indices=", negative_peaks_indices)
    negative_peaks = negative_peaks_indices[:peak_idx]
    negative_peak_APv = voltage[negative_peaks]
    #print("[debug]negative_peak_APv=", negative_peak_APv)
    mean_minV = np.mean(negative_peak_APv)
    #print("[debug]mean_minV=", mean_minV)
    
    return mean_period


#read the configure file and change the specific value
def update_csv_config(file_path, target_param, new_value):
    rows = []

    # read all lines
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == target_param:
                row[2] = str(new_value)
            rows.append(row)

    # re-write all lines
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("[debug]update csv finished!")

#read the configure file and change the specific value
def update_json_config(file_path, target_param1, target_param2):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    print(f"[debug]function's CL1 = {target_param1:.17f}")
    CL1 = Decimal(str(target_param1))
    CL2 = Decimal(str(target_param2))
    
    data["data_items"][0]["value"] = CL1
    data["data_items"][1]["value"] = CL2
    
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, cls=DecimalEncoder)
        
    print("[debug]update json finished!")
                

#some address 
model_name = "tpbinfer1"
params_dir = "/home/cdon822/Documents/GIT_files/CA_user/NEs_to_SAN/resources/"
out_dir = "../BoundaryCondition/"
model_dir = "../generated_models"
csv_ext = "_parameters.csv"
config_ext = "_obs_data.json"
txt_ext = "_summary.txt"
csv2_ext = "_results.csv"

filename1 = model_name + csv_ext
csv_config_addr = os.path.join(params_dir,filename1)
filename2 = model_name + txt_ext
txt_config_addr = os.path.join(out_dir,filename2)
filename3 = model_name + csv2_ext
out_config_addr = os.path.join(out_dir,filename3)
model_addr1 = os.path.join(params_dir,model_dir)
model_addr2 = model_addr1 + "/" + model_name + "/" + model_name + ".cellml"
filename_GT = params_dir + model_name + config_ext
print("[debug]address=",filename_GT)

#some string
std_str1 = "best fit params : [264.502056 0.5]"
std_str2 = "best cost       : 0.710"
std_str3 = "param id complete"

data_list0 = []
data_list = []
data_list2 = []
data_list3 = []
data_list4 = []

#for specific parameter, start auto run PLA algorithM
pv_name = 'k_M2bindGi_NES'
pv = 0.5
low = 1.0
high = 1.0125
reset_param_names = ['NES/ISO_init', 'NES/ACh_init']
reset_param_val = [0.5,50]
reset_param_val2 = [0.5,60]
obs_list = ['hrv/V']
times1 = np.arange(0,10.0001,0.0001)

while (abs(high - low)>0.0001):
    mid = (high + low)/2.0
    print("[debug]noise=",mid)
    pv_new = pv*mid
    data_list0.append(pv_new)
    update_csv_config(csv_config_addr, pv_name, pv_new)
    
    
    #call shell scripts, re-generate model
    subprocess.run(['bash', 'run_autogeneration.sh'])
    
    #run model, generate new results (include noise)
    x = SimulationHelper(model_addr2, 0.0001, 15, pre_time=0)
    x.set_param_vals(reset_param_names, reset_param_val)
    x.run()
    z10 = x.get_results(obs_list)
    z11 = z10[0][0]
    z12 = z11[50000:]
    z13 = z12.copy()
    #print("[debug]z=",len(z13))
    #print("[debug]times1=",len(times1))
    
    pred_CL1 = analyze_signal_from_data(times1, z13)
    print(f"[debug]CL1= {pred_CL1:.20f} ")
    
    x = SimulationHelper(model_addr2, 0.0001, 15, pre_time=0)
    x.set_param_vals(reset_param_names, reset_param_val2)
    x.run()
    z20 = x.get_results(obs_list)
    z21 = z20[0][0]
    z22 = z21[50000:]
    z23 = z22.copy()
    #print("[debug]z=",len(z23))
    #print("[debug]times1=",len(times1))
    
    
    pred_CL2 = analyze_signal_from_data(times1, z23)
    print(f"[debug]CL2= {pred_CL2:.20f} ")
    data_list4.append((pred_CL1,pred_CL2))
    
    #new results set as ground truth and updated in config file
    update_json_config(filename_GT, pred_CL1, pred_CL2)
    
    #after generate new GT, need reset the parameter file
    update_csv_config(csv_config_addr, pv_name, pv)
    #call shell scripts, re-generate model
    subprocess.run(['bash', 'run_autogeneration.sh'])
    
    #need save part of the log, so save all log first
    result = subprocess.run(['bash', './run_param_id.sh','16'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = result.stdout.strip().splitlines()
    last_two_lines = lines[-3:] if len(lines) >= 3 else lines
    str1 = next((s for s in last_two_lines if 'best fit params' in s), None)
    str2 = next((s for s in last_two_lines if 'best cost' in s), None)
    cost_value = float(str2.split(":")[1].strip())
    data_list3.append(cost_value)
    #print("[debug]str1=",str1)
    
    match = re.search(r"\[(.*?)\]", str1)
    if match:
        number_str = match.group(1)  
        numbers = np.fromstring(number_str, sep=' ')
        data_list2.append(numbers)
        print("[debug]predict NE/ACh=",numbers)  
    else:
        print("There are some errors in calibration process!")
    
    calibrate_err1 = abs(numbers[0] - reset_param_val[0])/reset_param_val[0]
    calibrate_err2 = abs(numbers[1] - reset_param_val[1])/reset_param_val[1]
    if (calibrate_err1<0.05 and calibrate_err2<0.05):
        low = mid
    else:
        high = mid
    data_list.append(mid)

print("[debug]data_list=",data_list)
print("[debug]data_list2=",data_list2)

boundary_left_ratio = mid
print("[debug]boundary_left_ratio=",boundary_left_ratio)

#save process data
with open("right_calibrated_log.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["pv","mid", "pred1", "pred2", "cost", "GT1", "GT2"]) 
    for d0, d1, (p1, p2), d3, (gt1,gt2) in zip(data_list0, data_list, data_list2, data_list3, data_list4):
        writer.writerow([d0, d1, p1, p2, d3, gt1, gt2])

print("[debug]stop in here!")
exit()

