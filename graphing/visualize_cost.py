import os
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

__author__: 'Steffen Schneider'


class Graph:
    def __init__(self, avg_cost = [], best_cost = []):
        self.fig = plt.figure()
        self.plot = self.fig.add_subplot(1,1,1)

        self.avg_cost = []
        self.best_cost = []


    def plot_cost(self):
        plt.plot(range(1, len(self.avg_cost)+1), self.avg_cost, label='avg')
        plt.plot(range(1, len(self.avg_cost)+1), self.best_cost, label='best')

        self.plot.legend()
        plt.xticks(range(0, len(self.avg_cost)+1))
        plt.grid()
        plt.show()

    def plot_cost_from_files(self, path):
        files = get_files_array(path)
        self.avg_cost, self.best_cost = transform_data(files)
        self.plot_cost()

    def add_costs(self, avg_cost, best_cost, animate=False):
        self.avg_cost.append(avg_cost)
        self.best_cost.append(best_cost)
        if animate: self.update_plot()

    def update_plot(self):
        self.plot.clear()
        avg_l = self.plot.plot([i for i in range(1, len(self.avg_cost)+1)], self.avg_cost, label='avg')
        best_l = self.plot.plot([i for i in range(1, len(self.best_cost)+1)], self.best_cost, label='best')
        
        self.plot.legend()
        plt.xticks(range(0, len(self.avg_cost)+1))
        plt.grid()
        plt.pause(0.0001)

    def start_animated_plotting(self):
        plt.ion()
        self.update_plot()
        
        


"""
Helper fuctions
"""
def files_collect(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def get_files_array(path):
    files = []
    for file in files_collect(path):
        files.append(file)
    return files

def transform_data(files):
    avg_cost = [0] * len(files)
    best_cost = [0] * len(files)
    for file in files:
        m = re.search('gen(\d{1,4})_cost(.\d*)_avg(.\d*)', file)
        best_cost[int(m.group(1))-1] = abs(int(m.group(2)))
        avg_cost[int(m.group(1))-1] = abs(int(m.group(3)))
    return avg_cost, best_cost

