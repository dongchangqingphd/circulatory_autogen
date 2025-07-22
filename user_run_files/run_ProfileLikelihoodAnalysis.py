import subprocess
import csv

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
                

#
pv_name = 'IC50_M2_NES'
pv = 725.39079288
delta_ratio = 0.1
iter_num = 100
analysis_delta = pv*delta_ratio
step_interval = pv*0.2/iter_num
start_value = pv*0.9
for i in range(1,iter_num):
    pv_new = start_value + i*step_interval
    
    update_csv_config('../resources/PLA1_parameters.csv', 'IC50_M2_NES', pv_new)
    print("[debug]pv_new=",pv_new)
    
     #call shell scripts
    subprocess.run(['bash', 'run_autogeneration.sh'])
    #need save part of the log, so save all log first
    result = subprocess.run(['bash', 'run_param_id.sh','16'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = result.stdout.strip().splitlines()
    last_two_lines = lines[-3:] if len(lines) >= 3 else lines
    #add style save log into the result file
    with open('PLA1_summary.txt', 'a') as file1:
        file1.write("=== Final Three Lines ===\n")
        file1.write(str(pv_new) + '\n')
        for line in last_two_lines:
            file1.write(line + '\n')
    

#subprocess.run(['python3', 'txt_trans.py'])

