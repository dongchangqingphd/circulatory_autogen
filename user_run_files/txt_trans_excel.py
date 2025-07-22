import re
#import pandas as pd
import csv

data = []
#read txt file
with open('correction_summary.txt', 'r') as f:
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
#df = pd.DataFrame(data, columns=["Value", "Cost", "Params"])
#df.to_excel("PLA1_results.xlsx", index=False)
flattened_data = []
for row in data:
    value, cost, params = row
    flattened_data.append([value, cost] + params)

# 写入 CSV 文件（可用 Excel 打开）
with open('PLA1_results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Value', 'Cost', 'Param1', 'Param2'])  # 修改标题根据 param 数量调整
    writer.writerows(flattened_data)
