import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def compute_peak_period(file_path):
    # 读取 CSV 文件
    df = pd.read_csv(file_path)
    
    # 确保列名正确
    df.columns = [col.strip().split('|')[0].strip() for col in df.columns]
    df = df.rename(columns={df.columns[0]: "time", df.columns[1]: "signal"})
    
    # 转换数据类型
    timet = df["time"].values.astype(float)
    voltage = df["signal"].values.astype(float)
    
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
    print("maxV=",mean_maxV)
    print("minV=",mean_minV)
    
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
    print("meanV=",mean_avgV)
    
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
    print("V_mean=",V_mean)
    
    
    # 绘制信号和峰值
    plt.figure(figsize=(10, 4))
    plt.plot(time, signal, label="Signal")
    plt.plot(peak_times_max, peak_values_max, "ro", label="Max Peaks")
    plt.plot(peak_times_min, peak_values_min, "bo", label="Min Peaks")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Signal with Detected Peaks")
    plt.legend()
    plt.grid()
    plt.show()
    
    print(f"Estimated Period from Peaks: {avg_period:.12f} s")
    print(f"Max Peaks: {peak_values_max}")
    print(f"Min Peaks: {peak_values_min}")
    print(f"Average Values per Period: {avg_values_per_period}")
    
    #ground true value
    maxV = 21.72285870290994
    minV = -58.40719047426184
    CL = 0.961750000000
    meanV = -40.22661476620413
    #calculate MSE
    cost1 = 1*pow((mean_maxV - maxV),2)
    cost2 = 1*pow((mean_minV - minV),2)
    cost3 = 10000*pow((avg_period - CL),2)
    cost4 = 1*pow((V_mean - meanV),2)
    cost_err = (cost1+cost2+cost3+cost4)/4
    print("cost=",cost_err)

    return avg_period, peak_values_max, peak_values_min, avg_values_per_period


# 调用函数
file_path = "/home/cdon822/Documents/GIT_files/circulatory_autogen/verify_infer_NEs/test.csv"  # 请替换为你的 CSV 文件路径
compute_peak_period(file_path)
