
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
        self.mpl_canvas = FigureCanvasTkAgg(fig, self)
        self.mpl_canvas.draw()
        self.mpl_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.mpl_canvas, self)
        self.toolbar.update()
        self.mpl_canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class MPLGraph(Figure):

    def __init__(self):
        Figure.__init__(self, figsize=(5, 5), dpi=100)
        self.plot = self.add_subplot(111)
        self.plot.plot([1, 2, 3, 4, 5, 6, 7], [4, 3, 5, 0, 2, 0, 6])

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
            proj_dir[f1]

def validateOpenROADsrc():
    pass

def validateOpenSCADsrc():
    pass

def validateXycescr():
    pass

def getProjectDirectory():
    pass

def selectSimulationDockerImage():
    pass

def selectPnrDockerImage():
    pass


## Button things

def callback_b1():
    folder_selected = filedialog.askdirectory()

def callback_b1(config):
    config["project_dir"].set(filedialog.askdirectory())

    refreshProjects(config["project_dir"].get())


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

    b1_dir = tk.Button(
            f1, 
            text="Projects", 
            command=lambda: callback_b1(prog_config))
    b1_dir.grid(column=0, row=1)
    #b1_dir.pack(ipadx=10, ipady=10)
    lb1_proj= tk.Listbox(
        f1,
        height=26,
        width=40,
        selectmode=tk.EXTENDED
    )
    lb1_proj.grid(column=0, row=3)

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

    f1.pack()
    w1.mainloop()






if __name__ == "__main__":
    main()