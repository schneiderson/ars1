import os
import re
import matplotlib.pyplot as plt
import numpy as np

__author__: 'Steffen Schneider'

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
        avg_cost[int(m.group(1))-1] = int(m.group(2))
        best_cost[int(m.group(1))-1] = int(m.group(3))
    return avg_cost, best_cost


def plot_cost(avg_cost, best_cost):
    fig = plt.figure()
    plt.plot(range(1, len(avg_cost)+1), avg_cost)
    plt.plot(range(1, len(avg_cost)+1), best_cost)
    plt.xticks(range(0, len(avg_cost)))
    plt.grid()
    plt.show()

def plot_cost_from_files(path):
    files = get_files_array(path)
    avg_cost, best_cost = transform_data(files)
    plot_cost(avg_cost, best_cost)
