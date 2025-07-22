import subprocess
import csv
import re
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
                

#for specific parameter, start auto run PLA algorithm
pv_name = 'IC50_M2_NES'
pv = 725.39079288
delta_ratio = 0.1
iter_num = 40
analysis_delta = pv*delta_ratio
step_interval = pv*0.2/iter_num
start_value = pv*0.9
for i in range(1,iter_num):
    pv_new = start_value + i*step_interval
    
    update_csv_config('../resources/PLA1_parameters.csv', pv_name, pv_new)
    print("[debug]pv_new=",pv_new)
    
     #call shell scripts
    subprocess.run(['bash', 'run_autogeneration.sh'])
    #need save part of the log, so save all log first
    result = subprocess.run(['bash', 'run_param_id.sh','16'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = result.stdout.strip().splitlines()
    last_two_lines = lines[-3:] if len(lines) >= 3 else lines
    #add style save log into the result file
    with open('../ProfileLikelihoodAnalysis/PLA1_summary.txt', 'a') as file1:
        file1.write("=== Final Three Lines ===\n")
        file1.write(str(pv_new) + '\n')
        for line in last_two_lines:
            file1.write(line + '\n')
    

#then, transform txt data into excel data, easy to copy
data = []
#read txt file
with open('../ProfileLikelihoodAnalysis/PLA1_summary.txt', 'r') as f:
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

with open('../ProfileLikelihoodAnalysis/PLA1_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Value', 'Cost', 'Param1', 'Param2'])  # 修改标题根据 param 数量调整
    writer.writerows(flattened_data)
    
