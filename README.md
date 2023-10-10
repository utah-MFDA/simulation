## MFDA simulation

This module is designed to communicate with the docker image used for MFDA simulation. This program acts as a bridge to run simulation programs. The docker image will require that the appropriate Verilog-AMS files can been built

The simulator can be interfaced from the the terminal python program in
frontend -> mfda_sim_cmd.py

It requires setting up a project directory that is organized as such

-- project_folder
 |_ project_1
    |_ project_1.v (verilog netlist)
    |_ project_1_length.xlsx
    |_ project_1_spec.csv
    |_ simTime.csv
    |_ devices.csv
 |_ project_2
    |_ ...
    
Examples can be found in testing/projects


