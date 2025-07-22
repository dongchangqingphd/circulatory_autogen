import subprocess
import csv
import re
import os
#import pandas as pd

#this script used for automatic run profile likelihood analysis for a set of calibrated parameters

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
                
#some address 
PLA_params_name = "tpbinfer1"
params_dir = "/home/cdon822/Documents/GIT_files/CA_user/NEs_to_SAN/resources/"
out_dir = "../ProfileLikelihoodAnalysis/"
csv_ext = "_parameters.csv"
txt_ext = "_summary.txt"
csv2_ext = "_results.csv"

filename1 = PLA_params_name + csv_ext
csv_config_addr = os.path.join(params_dir,filename1)
filename2 = PLA_params_name + txt_ext
txt_config_addr = os.path.join(out_dir,filename2)
filename3 = PLA_params_name + csv2_ext
out_config_addr = os.path.join(out_dir,filename3)
print("[debug]address=",out_config_addr)

#some string
std_str1 = "best fit params : [0.49765524 50.17161167]"
std_str2 = "best cost       : 0.000273676997816168"
std_str3 = "param id complete"

#for specific parameter, start auto run PLA algorithm
pv_name = 'ISO_init_NES'
pv = 0.49765524
delta_ratio = 0.2
iter_num = 10
analysis_delta = pv*delta_ratio
step_interval = pv*2*delta_ratio/iter_num
start_value = pv*(1-delta_ratio)
for i in range(1,iter_num+2):
    pv_new = start_value + (i-1)*step_interval
    if abs(pv_new - pv) < 1e-7:
        with open(txt_config_addr, 'a') as file1:
            file1.write("=== Final Three Lines ===\n")
            file1.write(str(pv_new) + '\n')
            file1.write(std_str1 + '\n')
            file1.write(std_str2 + '\n')
            file1.write(std_str3 + '\n')
        continue
            
    update_csv_config(csv_config_addr, pv_name, pv_new)
    print("[debug]pv_new=",pv_new)
    
     #call shell scripts
    subprocess.run(['bash', 'run_autogeneration.sh'])
    #need save part of the log, so save all log first
    result = subprocess.run(['bash', 'run_param_id.sh','16'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = result.stdout.strip().splitlines()
    last_two_lines = lines[-3:] if len(lines) >= 3 else lines
    #add style save log into the result file
    print("[debug]save_addr=",txt_config_addr)
    with open(txt_config_addr, 'a') as file1:
        file1.write("=== Final Three Lines ===\n")
        file1.write(str(pv_new) + '\n')
        for line in last_two_lines:
            file1.write(line + '\n')
    

#then, transform txt data into excel data, easy to copy
data = []
#read txt file
with open(txt_config_addr, 'r') as f:
    lines = f.readlines()

i = 0
while i < len(lines):
    line = lines[i].strip()

    if line.startswith("===") and "Final Three Lines" in line:
        # extract next 3 lines
        value_line = lines[i + 1].strip()
        params_line = lines[i + 2].strip()
        cost_line = lines[i + 3].strip()

        # extract values
        try:
            value = float(value_line)
        except ValueError:
            i += 1
            continue

        # extract parameters
        params_match = re.search(r'\[(.*?)\]', params_line)
        if params_match:
            params_str = params_match.group(1)
            params = [float(x) for x in params_str.strip().split()]
        else:
            params = []

        # extract parameters
        cost_match = re.search(r'best cost\s*:\s*([-+]?\d*\.\d+|\d+)', cost_line)
        cost = float(cost_match.group(1)) if cost_match else None

        # save parameters
        data.append([value, cost, params])

        i += 4  
    else:
        i += 1

# write into Excel
flattened_data = []
for row in data:
    value, cost, params = row
    flattened_data.append([value, cost] + params)

with open(out_config_addr, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Value', 'Cost', 'Param1', 'Param2'])  # 修改标题根据 param 数量调整
    writer.writerows(flattened_data)
    
