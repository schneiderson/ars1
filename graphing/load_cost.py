import visualize_cost as vc
import os
import re
import argparse

__author__ = 'Steffen Schneider'

def determin_latest(files):
    """
    find latest cost filse in directory
    """
    latest_date = 0
    latest_time = 0
    for file in files:
        m = re.search('weights_(\d*)-(\d*)', file)
        if ( m == None ): continue
        if( latest_date < int(m.group(1)) ): 
            latest_date = int(m.group(1))
            latest_time = int(m.group(2))
        elif( latest_date == int(m.group(1)) ):
            if( latest_time < int(m.group(2)) ): 
                latest_time = int(m.group(2))
    return "weights_" + str(latest_date) + "-" + str(latest_time)

def get_directories(path):
    return [o for o in os.listdir(path) if os.path.isdir(os.path.join(path,o))]

# get cli arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help='directory to use',action='store')
args = parser.parse_args()

# create graph
graph = vc.Graph()

# load cost from directory
if args.directory:
    graph.plot_cost_from_files(args.directory)
else:
    files = get_directories('weights/')
    latest = determin_latest(files)
    graph.plot_cost_from_files("weights/" + latest)



