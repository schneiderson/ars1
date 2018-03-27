# Autonomous Robotic Systems assignment 1

This is the OLD readme for assignment 1 on Genetic Algorithm

## Group 2
- Steffen Schneider
- Olve Drageset
- Andre Gramlich
- Camiel Kerkhofs

(Specific code authorship is indicated at the top of each file)

---
## Python 3.6 dependencies
- numpy
- matplotlib
- pygame
---

## Execution
To run our best performing model execute the main.py file with the following command:
```
python main.py -m 1
```
To run a new simulation, execute the main.py file with the following command:
```
python main.py -m 2
```

If you wish to change any simulation settings, edit the main.py file before execution


### Testing
how to run unit tests:
```
python -m unittest tests.ann_test
python -m unittest tests.kinematicstest
python -m unittest tests.robottest
```


### Plotting
to show avg and best cost in a graph run: (Only works if you have ran a simulation before)
```
python graphing/load_cost.py
```
to load a specific result from a directory run: (Relative path to simulation results)
```
python graphing/load_cost.py -d <path>
```
