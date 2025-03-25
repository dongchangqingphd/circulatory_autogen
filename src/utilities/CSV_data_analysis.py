from scipy.signal import find_peaks
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. 读取 CSV 文件
file_path = "/home/cdon822/Documents/GIT_files/circulatory_autogen/verify_infer_NEs/SANHR5_3.csv"  # 替换成你的文件名
data = pd.read_csv(file_path)
data.columns = [col.strip().split('|')[0] for col in data.columns]



# Extract time and voltage
time = data.iloc[:, 0].values
voltage = data.iloc[:, 1].values

start_time = 2.0  # 从2秒开始
mask = time >= start_time  # 过滤数据
time_filtered = time[mask]
voltage_filtered = voltage[mask]
max_voltage = np.max(voltage_filtered)
min_voltage = np.min(voltage_filtered)
print("max_V=",max_voltage)
print("min_V=",min_voltage)


# Detect peaks with minimum spacing (~0.5s, adjust as needed)
dt = np.mean(np.diff(time_filtered))
peaks, _ = find_peaks(voltage_filtered, distance=int(0.5 / dt))  

# Compute period
if len(peaks) > 1:
    peak_intervals = np.diff(time_filtered[peaks])
    estimated_period_time = np.mean(peak_intervals)
else:
    estimated_period_time = None  # If no peaks detected
    
frequency = 1.0/estimated_period_time
print("frequency=",frequency)    
print("period_time=",estimated_period_time)  

# Plot signal with detected peaks
#plt.figure(figsize=(10, 4))
#plt.plot(time, voltage, 'r', label="Voltage Signal")
#plt.plot(time[peaks], voltage[peaks], 'bo', label="Detected Peaks")  # Mark peaks
#plt.xlabel("Time (s)")
#plt.ylabel("Voltage (mV)")
#plt.title("Peak Detection for Period Estimation")
#plt.legend()
#plt.grid(True)
#plt.show()

# Print result
print(f"Estimated period (from peaks): {estimated_period_time:.4f} s")
