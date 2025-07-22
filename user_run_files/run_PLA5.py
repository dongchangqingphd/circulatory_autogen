import subprocess
import csv
import re
import os
import shutil
import yaml
#import pandas as pd
root_dir = os.path.join(os.path.dirname(__file__), '../')
user_inputs_dir= os.path.join(root_dir, 'user_run_files')

#this script used for automatic run profile likelihood analysis for a set of calibrated parameters

#read the configure file and change the specific value
def update_csv_config(file_path, target_param, new_value):
    rows = []
    current_dir1 = os.path.dirname(os.path.abspath(__file__))
    print("current address: ", current_dir1)
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
                
def auto_run_ProfileLikelihoodAnalysis(model_params_name,pv_name,pv,calibrated_model_addr):
    params_dir = "../resources/"
    out_dir = "../ProfileLikelihoodAnalysis/"
    csv_ext = "_parameters.csv"
    txt_ext = "_summary.txt"
    csv2_ext = "_results.csv"
    std_str1 = "best fit params : [1.14428552e+00 6.00000000e+02]"
    std_str2 = "best cost       : 0.757543867507327"
    std_str3 = "param id complete"
    filename1 = model_params_name + csv_ext
    #csv_config_addr = os.path.join(params_dir,filename1)
    #use specific address rather than local address
    csv_config_addr = os.path.normpath(os.path.join(calibrated_model_addr,params_dir,filename1))
    
    filename2 = model_params_name + txt_ext
    #txt_config_addr = os.path.join(out_dir,filename2)
    txt_config_addr = os.path.normpath(os.path.join(calibrated_model_addr,out_dir,filename2))
    filename3 = model_params_name + csv2_ext
    #out_config_addr = os.path.join(out_dir,filename3)
    out_config_addr = os.path.normpath(os.path.join(calibrated_model_addr,out_dir,filename3))
    print("[debug]address=",csv_config_addr)
    

    delta_ratio = 0.3
    iter_num = 8
    analysis_delta = pv*delta_ratio
    step_interval = pv*delta_ratio*2/iter_num
    start_value = pv*(1-delta_ratio)
    
    #for specific parameter, start auto run PLA algorithm
    for i in range(1,iter_num+2):
        pv_new = start_value + (i-1)*step_interval
        if abs(pv_new - pv) < 1e-6:
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print("current address: ", current_dir)
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
        writer.writerow(['Value', 'Cost', 'Param1', 'Param2']) 
        writer.writerows(flattened_data)
        
#read the csv file and save the specific parameters
def read_csv(file_path):
    #rows = []
    results = []
    # read all lines
    with open(file_path, 'r') as f:
        reader = csv.reader(f)  
        next(reader)    #first line is name, so ignore it
        for row in reader:
            #print("[debug]row=",row[0])
            results.append(row)

    # re-write all lines
    return results

#some address 
analysis_file_addr = "/home/cdon822/Documents/GIT_files/CA_user/NEs_to_SAN/test/test.csv" #careful the style
calibrated_model_addr = "/home/cdon822/Documents/GIT_files/CA_user/NEs_to_SAN/resources"
calibrated_model_name = "tp"

#read csv files, get need Profile Likelihood Analysis parameters
PLA_params = read_csv(analysis_file_addr)
num_params = len(PLA_params)

pi = 0
while pi<num_params:
    pv_name = PLA_params[pi][0]
    pv = float(PLA_params[pi][2])
    print("[debug]pv=",pv)
    PLA_params_name = "PLA_" + pv_name
    
    #read parameter file and resave another name match to process PLA algorithm
    file1_param = calibrated_model_addr + "/" + calibrated_model_name + "_parameters.csv"
    new_file1 = calibrated_model_addr + "/" + PLA_params_name + "_parameters.csv"
    
    rows = []
    # read all lines
    with open(file1_param, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # re-write all lines
    with open(new_file1, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    #read vessel_connect file and resave another name match to process PLA algorithm
    file3_param = calibrated_model_addr + "/" + calibrated_model_name + "_vessel_array.csv"
    new_file3 = calibrated_model_addr + "/" + PLA_params_name + "_vessel_array.csv"
    
    rows = []
    # read all lines
    with open(file3_param, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # re-write all lines
    with open(new_file3, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    #copy predict and ground true file save another name match to process PLA algorithm
    file2_param = calibrated_model_addr + "/" + calibrated_model_name + "_obs_data.json"
    new_file2 = calibrated_model_addr + "/" + PLA_params_name + "_obs_data.json"
    
    shutil.copyfile(file2_param, new_file2)  #directly copy
        
    #read calibrate model and resave another name match to process PLA algorithm
    file4_param = calibrated_model_addr + "/" + calibrated_model_name + "_params_for_id.csv"
    new_file4 = calibrated_model_addr + "/" + PLA_params_name + "_params_for_id.csv"
    rows = []
    analysis_name = pv_name[:-4]
    # read all lines
    with open(file4_param, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            #print("[debug]param=",row[1])
            if row[1] == analysis_name:
                continue
            rows.append(row)
    # re-write all lines
    with open(new_file4, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    
    
    #before for each parameter PLA, need modify corresponding user_inputs.yaml file
    key_words1 = "file_prefix:"
    replace_words1 = "file_prefix: "+PLA_params_name
    key_words2 = "input_param_file:"
    replace_words2 = "input_param_file: "+PLA_params_name + "_parameters.csv"
    key_words3 = "param_id_obs_path:"
    #replace_words3 = "file_prefix: "+PLA_params_name
    inp_data_dict=None
    if inp_data_dict is None:
        with open(os.path.join(user_inputs_dir, 'user_inputs.yaml'), 'r') as file:
            inp_data_dict = yaml.load(file, Loader=yaml.FullLoader)
        if "user_inputs_path_override" in inp_data_dict.keys() and inp_data_dict["user_inputs_path_override"]:
            if os.path.exists(inp_data_dict["user_inputs_path_override"]):
                overwrite_yaml = inp_data_dict["user_inputs_path_override"]
                with open(overwrite_yaml, 'r') as file:
                    lines = file.readlines()
                    inp_data_dict = yaml.load(file, Loader=yaml.FullLoader)
                
                #replace key words line
                new_lines = []
                for line in lines:
                    if key_words1 in line:
                        new_lines.append(replace_words1+"\n")
                    elif key_words2 in line:
                        new_lines.append(replace_words2+"\n")
                    elif key_words3 in line:
                        last_slash_index = line.rfind('/')
                        str1 = line[:last_slash_index]
                        replace_words3 = str1 + "/" + PLA_params_name + "_obs_data.json"
                        new_lines.append(replace_words3+"\n")
                    else:
                        new_lines.append(line)
                #rewrite the yaml file
                with open(overwrite_yaml, 'w') as file:
                    file.writelines(new_lines)
            else:
                print(f"User inputs file not found at {inp_data_dict['user_inputs_path_override']}")
                print("Check the user_inputs_path_override key in user_inputs.yaml and set it to False if "
                        "you want to use the default user_inputs.yaml location")
                exit()

    
    print("[debug]file=",overwrite_yaml)
    
    #also need to change user_inputs.yaml file
    
    
    auto_run_ProfileLikelihoodAnalysis(PLA_params_name,pv_name,pv,calibrated_model_addr)
    pi = pi + 1
    

PLA_params_name = "PLA1"
pv_name = 'EC50_beta1_NES'
pv = 1.14428552




#auto_run_ProfileLikelihoodAnalysis(PLA_params_name,pv_name,pv)
#not finish yet, need test








