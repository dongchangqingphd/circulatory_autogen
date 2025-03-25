#import opencor as oc
import sys
import numpy as np
import csv
#from PyQt5.QtWidgets import QApplication
import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import paperPlotSetup
matplotlib.use('Agg')
import xml.etree.ElementTree as ET
from lxml import etree

# TODO 
#preset some address, such as input model address, results saved address
file_path = "/home/cdon822/Documents/GIT_files/circulatory_autogen/module_config_user/TEST_modules.cellml"
Outputfile_address = "/home/cdon822/Documents/GIT_files/circulatory_autogen/module_config_user/new_module_config.json"

#read file
tree = etree.parse(file_path)
root = tree.getroot()
ns = {"cellml": "http://www.cellml.org/cellml/1.1#"}

print(f"=== OpenCOR Parsed CellML File: {file_path} ===\n")

# Print model name
model_name = root.attrib.get("name", "Unnamed Model")
print(f"Model Name: {model_name}\n")

# Iterate through components
for component in root.findall("cellml:component", ns):
    comp_name = component.attrib.get("name", "Unnamed Component")
    print(f"[Component] {comp_name}")

    # Iterate through variables
    for variable in component.findall("cellml:variable", ns):
        var_name = variable.attrib.get("name", "Unnamed Variable")
        units = variable.attrib.get("units", "dimensionless")
        print(f"  - Variable: {var_name}, Units: {units}")

    print("")  # Add space between components

    # Print connections (if any)
for connection in root.findall("cellml:connection", ns):
    print("[Connection]")
    for map_variable in connection.findall("cellml:map_variables", ns):
        var1 = map_variable.attrib.get("variable_1", "Unknown")
        var2 = map_variable.attrib.get("variable_2", "Unknown")
        print(f"  - {var1} <--> {var2}")
    print("")

