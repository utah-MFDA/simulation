

The central idea for this project is to create an open-source 
design automation tool for microfluidics. This project currently
uses HSPICE as the main simulator, but is currently being 
adapted to run on open-source simulators such as NgSPICE and
Xyce. The simulator's goal is to solve the fluid and chemical
solutions for a microfluidic system to aid in evaluating and
validating system performance. The tool uses several Python 
scripts to translate the Verilog (.v) netlist files to SPICE
(.sp) files to be used in simulation. The program then upload
the SPICE files to a remote server with HSPICE to run the 
nessary simulations of the target microfluidic chip. The SPICE 
files compiles Verilog-AMS (.va, included in this repo) of defined 
standard and parameteric cells to model the system.

### Getting Started 


### General Flow

To complete the flow the general steps need to be taken
1. create a new directory in the following path
    - /Continuous/V2Va_Parser/testFiles/(designName)
2. in the folder above the following files need to be included
    - devices.csv - this file contains information relating 
    to the controlling pumps at the inlets of the chip. This
    included pressure and flowrates of the pump (where 
    applicable) in the format pressure=xxx and flowRate=xxx
    - dimm.csv - the file contains information about the 
    routing channels connecting the components in the 
    microfluidic device in number of pixels.
    - (design)_spec.csv - this file specifies the inlet
    concentrations of solutions and the expected outputs and 
    at what outlet port.
    - (design).v - this file is the Verilog HDL file of the device
    used in additionally in place and routing.
3. After the files are added the simulation can be run with simMain.py
    '''
    python simMain.py
    '''
