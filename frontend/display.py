
import tkinter as tk
from tkinter import filedialog

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import docker

## local imports
import sys, os
sys.path.insert(1, os.getcwd())
import runMFDASim

class GraphPage(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.title_label = tk.Label(self, text="Graph Page Example")
        self.title_label.pack()
        #self.pack()

    def add_mpl_figure(self, fig):
        self.fig = fig
        self.mpl_canvas = FigureCanvasTkAgg(fig, self)
        self.mpl_canvas.draw()
        self.mpl_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.mpl_canvas, self)
        self.toolbar.update()
        self.mpl_canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_mpl_figure(self, x, y):
        self.fig.update_plot_data(x, y)
        self.mpl_canvas.draw()

class MPLGraph(Figure):

    def __init__(self):
        Figure.__init__(self, figsize=(5, 5), dpi=100)
        self.plot = self.add_subplot(111)
        self.plot.plot([1, 2, 3, 4, 5, 6, 7], [4, 3, 5, 0, 2, 0, 6])

    def update_plot_data(self, x, y):
        self.plot.clear()
        self.plot.plot(x, y)


def get_docker_containers():
    client = docker.from_env()
    return [d.name for d in client.containers.list()]

# need some kind of global var for this
def refreshProjects():
    pass

def refreshProjects(proj_file):
    
    proj_dir = {}

    for f1 in os.listdir(proj_file):
        _f1 = proj_file+"/"+f1
        if os.path.isdir(_f1):
            proj_dir[f1] = {} 

            proj_dir[f1]['base'] = _f1

            validateNetListFile(proj_file, f1, proj_dir)

            validateOpenROADsrc(proj_file, f1, proj_dir)

            validateOpenSCADsrc(proj_file, f1, proj_dir)

            validateXycescr(proj_file, f1, proj_dir)

            getXyceFiles(proj_file, f1, proj_dir)

    return proj_dir

def refreshProjectOptions(config, optionmenu, optionVar):
    
    if not isinstance(optionmenu, tk.OptionMenu):
        return
    
    optionmenu['menu'].delete('0',tk.END)

    if 'projects' in config and len(config['projects']) > 0:
        optionmenu.configure(state='active')
        for proj in config['projects']:
            optionmenu['menu'].add_command(label=proj, command=tk._setit(optionVar, proj))

    else:
        optionmenu.configure(state='disabled')

def searchForFileExt(wd, ext, baseDir=True):
    fileList = []
    for f in os.listdir(wd):
        f = wd+"/"+f
        if os.path.isdir(f):
            fileList += searchForFileExt(wd+"/"+f, ext)
        if os.path.isfile(f):
            f_ext = f.split(".")[-1]
            if f_ext == ext:
                if not baseDir:
                    fileList += [os.path.basename(f)]
                else:
                    fileList += [f]

    return fileList

def validateNetListFile(wd, proj_name, proj_config):
    proj_wd = wd+"/"+proj_name

    if os.path.isfile(proj_wd+"/"+proj_name+".v"):
        return True
    return False

def validateOpenROADsrc(wd, proj_name, proj_config):
    pass

def validateOpenSCADsrc(wd, proj_name, proj_config):
    pass

def validateXycescr(wd, proj_name, proj_config):
    
    proj_wd = wd+"/"+proj_name
    proj = proj_config[proj_name]

    #check for results folder
    results_dir = proj_wd+ \
                   "/results"
    
    if (os.path.isdir(results_dir)):
        proj['results'] = results_dir

    #check for spice folder
    spice_dir = proj_wd+ \
                   "/spiceFiles"
    
    if (os.path.isdir(spice_dir)):
        proj['spiceFiles'] = spice_dir

    # check devices file
    devices_file = proj_wd+ \
                   "/devices.csv"
    
    if os.path.isfile(devices_file):
        proj['devices'] = devices_file

    # chech spec file
    spec_file = proj_wd+ \
                   "/"+proj_name+"_spec.csv"

    if os.path.isfile(spec_file):
        proj['spec'] = spec_file

    # check time file
    time_file = proj_wd+ \
                   "/simTime.csv"
    
    if os.path.isfile(time_file):
        proj['time'] = time_file

    os.path.isfile(time_file)

def getXyceFiles(wd, proj_name, proj_config):

    proj_wd = wd+"/"+proj_name
    proj = proj_config[proj_name]

    results_ext = "prn"
    # inspect results dir
    if 'results' in proj:
        results_files = searchForFileExt(
            proj["results"], 
            results_ext,
            baseDir=False)
        proj["result_files"] = results_files

    spice_ext = "cir"
    # inspect spiceFiles dir
    if 'spiceFiles' in proj:
        spice_files = searchForFileExt(
            proj["spiceFiles"], 
            spice_ext,
            baseDir=False)
        proj["spice_files"] = spice_files

def getProjectDirectory():
    pass

def selectSimulationDockerImage():
    pass

def selectPnrDockerImage():
    pass


## Option Menu callback
"""
For config the project files are under
    config["projects"][$proj]["result_files"]
"""
def updateListBox(config, optionVar, listboxVar):
    #if not isinstance(listboxVar, tk.Variable): 
    #    print("wrong list type")
    #    return


    selectProj = optionVar.get()
    if selectProj in config['projects']:
        if 'result_files' in config['projects'][selectProj]: 
            listboxVar.set(config['projects'][selectProj]['result_files'])
            
                

## Listbox plot the selected file

def updatePlot_from_list(project, selectedFile, config, plotframe):

    project = project.get() 
    if (project in config['projects'] and  
        'result_files' in config['projects'][project]):
        if selectedFile in config['projects'][project]['result_files']:
            rFile = "/".join([
                config['projects'][project]['results'],
                selectedFile    
            ])

            rData = runMFDASim.load_xyce_results(
                config['projects'][project]['results'],
                [selectedFile]
                )[0]
            
            # returns column names
            rDataKeys = list(rData)

            for k in rDataKeys:
                if k == "TIME":
                    continue
                else:
                    plotframe.update_mpl_figure(rData["TIME"], rData[k])
            

def updatePlot():
    pass

## Button things

def callback_b1():
    folder_selected = filedialog.askdirectory()

def callback_b1(config, optionmenu, optionVar):
    config["project_dir"].set(filedialog.askdirectory())

    config["projects"] = refreshProjects(config["project_dir"].get())

    refreshProjectOptions(config, optionmenu, optionVar)

def main():

    ##################################
    # windows definitions
    w1 = tk.Tk()
    w1.resizable(False, False)
    w1.title("MFDA Application")

    # size
    f1 = tk.Frame(w1, height=400, width=800)
    


    #### configurations impormation
    prog_config = {}
    prog_config['project_dir'] = tk.StringVar(w1, "project directory")
    
    #### Directory selection
    l1_dir = tk.Label(
        f1,
        #text="test text",
        textvariable=prog_config['project_dir'],
        height=2,
        width=50
    )
    l1_dir.grid(column=0, row=0)
    #l1_dir.pack(ipadx=10, ipady=10)

    listboxProjVar = tk.Variable()

    lb1_proj= tk.Listbox(
        f1,
        listvariable=listboxProjVar,
        #command=lambda: updatePlot(
        #    projectVar,
        #    lb1_proj.curselection(),
        #    prog_config, 
        #    fig),
        height=26,
        width=40,
        selectmode=tk.EXTENDED
    )
    lb1_proj.grid(column=0, row=3)


    projectVar = tk.StringVar(w1)
    projectVar.set("Project List")
    #projectVar.trace_add('wirte', lambda *args: print(projectVar.get()))
    projectVar.trace_add('write', lambda *args: updateListBox(prog_config, projectVar, listboxProjVar))

    om1_proj = tk.OptionMenu(
    #om2_docker = tk.Listbox(
        f1,
        projectVar,
        " ",
        command=lambda: updateListBox(prog_config, projectVar, listboxProjVar)
        #height=1,
        #width=25
    )
    om1_proj.grid(column=0, row=2)
    om1_proj.configure(state="disabled")


    b1_dir = tk.Button(
            f1, 
            text="Projects", 
            command=lambda: callback_b1(prog_config, om1_proj, projectVar))
    b1_dir.grid(column=0, row=1)
    #b1_dir.pack(ipadx=10, ipady=10)

    


    

    ######
    ## Docker buttons
    l2_docker = tk.Label(
        f1,
        text="Docker Image status: --------"
    )
    l2_docker.grid(column=1, row=1)
    
    docker_container_list = get_docker_containers()
    dockerVar = tk.StringVar(w1)
    dockerVar.set("container")

    om2_docker = tk.OptionMenu(
    #om2_docker = tk.Listbox(
        f1, 
        dockerVar,
        *docker_container_list
    )
    om2_docker.grid(column=1, row=0)

    # start container
    b2_docker_start = tk.Button(
        f1,
        text="Start",
    )
    b2_docker_start.grid(column=1, row=2)

    # stop container
    b2_docker_stop  = tk.Button(
        f1,
        text="Stop",
    )
    b2_docker_stop.grid(column=1, row=2)

    ######
    # Figure
    fig = MPLGraph()

    graph_page = GraphPage(f1)
    graph_page.add_mpl_figure(fig)
    graph_page.grid(column=1, row=3)

    # plot button
    b3_plot = tk.Button(
        f1,
        text="Plot",
        command=lambda: updatePlot_from_list(
            projectVar,
            listboxProjVar.get()[lb1_proj.curselection()[0]],
            prog_config, 
            #fig,
            graph_page
        ),
    )
    b3_plot.grid(column=0, row=4)

    f1.pack()
    w1.mainloop()






if __name__ == "__main__":
    main()