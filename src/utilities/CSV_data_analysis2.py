import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft

file_path = "/home/cdon822/Documents/GIT_files/circulatory_autogen/verify_infer_NEs/test.csv"  # 替换成你的文件名
data = pd.read_csv(file_path)
data.columns = [col.strip().split('|')[0] for col in data.columns]


# Extract time and voltage
time2 = data.iloc[:, 0].values
voltage = data.iloc[:, 1].values

start_time = 5.0  # 从X秒开始
mask = time2 >= start_time  # 过滤数据
time = time2[mask]
signal = voltage[mask]


max_voltage = np.max(signal)
min_voltage = np.min(signal)
print("max_V=",max_voltage)
print("min_V=",min_voltage)


# 计算采样率（假设时间间隔均匀）
dt = np.mean(np.diff(time))  # 计算时间步长
fs = 1 / dt  # 计算采样频率

# 计算 FFT
n = len(signal)
freqs = np.fft.fftfreq(n, d=dt)  # 计算频率
fft_values = np.abs(fft(signal))  # 计算 FFT 幅值

# 找到主频率
peak_freq = freqs[np.argmax(fft_values[1:]) + 1]  # 忽略 DC 分量（索引 0）
period = 1 / peak_freq if peak_freq != 0 else np.nan  # 计算周期

# 打印结果
print(f"信号主频率: {peak_freq:} Hz")
print(f"信号周期: {period:} 秒")

# 绘制 FFT 结果
plt.figure(figsize=(8, 4))
plt.plot(freqs[:n // 2], fft_values[:n // 2])  # 仅绘制正频率部分
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("FFT Spectrum")
plt.grid()
plt.show()


#gold standard
maxV = 20.8420469077498
minV = -58.369872350222
CL = 0.5555666666666668

#calculate MSE
cost1 = 1*pow((max_voltage - maxV),2)
cost2 = 1*pow((min_voltage - minV),2)
cost3 = 10000*pow((period - CL),2)
cost4 = 1*pow((peak_freq - 0.9091818181818181),2)
cost_err = (cost1+cost2+cost3)/3
print("cost=",cost_err)
