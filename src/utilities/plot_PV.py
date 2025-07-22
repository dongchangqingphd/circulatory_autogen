#import opencor
import sys
from opencor_helper import SimulationHelper
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

# call model
file_path = "/home/cdon822/Documents/weekly-report/721/721-assignment1/BG_LV.cellml"

# set simulation configuration
simulation_time = 30 
simulation_dt = 0.001
obs_list = ['Left_ventricle/u_P','Left_ventricle/Q_LV']

# run simulation
simulation = SimulationHelper(file_path, simulation_dt, simulation_time, pre_time=0)
simulation.run()

# get simulation results
results = simulation.get_results(obs_list)
print("[debug]results=",results)

#time = results['environment']['time']
pressure = results[0]
volume = results[1]

# plot Pressure-Volume loop and save
save_addr1 = "/home/cdon822/Documents/weekly-report/721/721-assignment1/others/Pressure_Volume-simulation_results.png"
plt.figure(figsize=(8,6))
plt.plot(volume, pressure,marker='.',linestyle='-',color='r',label='calibrated')
plt.xlabel('Volume (mL)')
plt.ylabel('Pressure (mmHg)')
plt.title('Left Ventricle Pressure-Volume Loop')
plt.grid(True)
plt.savefig(save_addr1,bbox_inches='tight')
plt.show()

