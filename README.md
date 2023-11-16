## MFDA simulation

This module is designed work with automation tools for microfluidic design using open-source electronic design automation (EDA) tools. This tool use the Xyce tool from Sandia to create system-level models of a set of standard components. The supported models are a set of flow control valves and various sizes of serpentine channels and arbitrary channels. It has been designed to work along side the place and routing tool (https://github.com/utah-MFDA/place_and_route). The target for the code has been developed to work with a complementary docker tool ().

### Required Software


For running on the host machine the first thing to do after cloning this repo is...

1) Clone the Xyce repo and build the software as described with ADMS support to build the Verilog-AMS files. This will require additionally building the Trillinos and suitesparse libraries.

2) Clone the component library repo https://github.com/utah-MFDA/component_library. The libraries will need to be built which can be done by running make from the component_library/VerilogA 

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


