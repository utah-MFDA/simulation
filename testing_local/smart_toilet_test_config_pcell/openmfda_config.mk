DISTRIB_V = 0.0.0

export DESIGN_NAME     	= smart_toilet

export FLOW_VARIANT     = sim_pcell

CONFIG_ROOT = ../tools/simulation/testing_local/smart_toilet_test_config_pcell
PLATFORM = h.r.3.3

export VERILOG_FILES 	= ./$(CONFIG_ROOT)/smart_toilet.v
export SDC_FILE      	= ./$(CONFIG_ROOT)/omfda_configs/constraint.sdc

export IO_CONSTRAINTS	= ./$(CONFIG_ROOT)/omfda_configs/io_constraints.tcl

export GLOBAL_PLACEMENT_ARGS_FILE = ./$(CONFIG_ROOT)/omfda_configs/global_place_args.tcl

export TECH_LEF = ./platforms/$(PLATFORM)/lef/$(PLATFORM)_$(DISTRIB_V).tlef
export SC_LEF   = ./platforms/$(PLATFORM)/lef/$(PLATFORM)_merged_$(DISTRIB_V).lef

export SIMULATION_CONFIG = ./$(CONFIG_ROOT)/simulation.config

export SCAD_LIB = $(PLATFORM_DIR)/pdk/scad_lib

export SCAD_INCLUDE_FILES = $(SCAD_LIB)/polychannel_v2.scad \
	$(SCAD_LIB)/lef_helper.scad \
	$(SCAD_LIB)/lef_scad_config.scad