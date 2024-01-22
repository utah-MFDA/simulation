## MFDA simulation

This is a microfluidic design automation (MFDA) module developed to simulate using a modified nodal analysis, based on using Xyce ciruit simulator. This module to run on a host machine with Xyce or  communicate with the docker image with Xyce for MFDA simulation. This program acts as a bridge to run simulation programs, as well as translate the verilog netlist files to the nessary format for Xyce.

## Getting started 

You can copy the template folder to get all the nessary files for the simulator. Just change the name of the netlist file <device_name>.v and change the module name inside the netlist file to match.

First you will need to make sure you have done one of the following:
1) Install XYce on the host machine with support for external libraries, or

2) For those running the simulator within a docker container, you will first need to make sure you have docker installed and the nessary docker image downloaded, bgoenner/mfda_xyce.

After that edit the files in your new device directory, make sure the name of the device directory is the same as the verilog netlist file without .v and the top-most module within the verilog file.

Create a running docker container with 
```
$ docker run -dit bgoenner/mfda_xyce
```
Take note of the name of the docker container by running
```
docker ps
```

The simulator can then simply be ran with
```
python3 runMFDASim.py <args>
```

There are a lot of necessary arguments to run the simulator listed here

For local Xyce builds make sure to include
```
--netlist
```
   The name of the verilog netlist, without the path

```
--sim_dir
```
   The path to the simulation files

```
--sim_file
```
   Directory of the simulation config file, usually simulation.config


```
--design
```
   The name of the device, usually the verilog file without the extension


```
--cir_config
```
   configurion of the .v to .cir translation


```
--lib
```
   A list of valid library components in csv format

```
--docker_container
```
   (docker) The name of the docker container used for the simulator

```
--xyce_local
```
   (xyce host) Set True to use Xyce from the local machine. Make sure to initialize the xyce_run submodule, can create a configuration. 

```
--eval_file

```
   (optional) file used for error calculations


```
--length_file
```
   (optional) file used for channels for connecting length


```
--plot
```
   (optional) add True after this argument to automatically plot the outputs

