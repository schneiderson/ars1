# Autonomous Robotic Systems assignment 2

This is the NEW readme for assignment 2 on Kalman Filters

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
To get a demonstration of the kalman filter, run
```
python main.py
```
To see a plot of the errors over time of the odometry prediction,
sensor data belief, and Kalman Filter belief, pause the simulation with SPACE.

### Testing
how to run unit tests:
```
python -m unittest tests.ann_test
python -m unittest tests.kinematicstest
python -m unittest tests.robottest
```


### Plotting

plot odometry sampling
```
python -m graphing.visualize_sampling
```
![Setting relativele low noise](etc/img/low_errors.png?raw=true "Low error")
relatively low error ( noise=[.01, .02, .02, .02] )

You can set the noise by passing it as comma separated list to parameter -n
```
python -m graphing.visualize_sampling --n '0.03,0.03,0.2,0.2'
```
![high translational error](etc/img/high_trans_error.png?raw=true "high translational error")
high translational error

```
python -m graphing.visualize_sampling --n '0.1,0.2,0.05,0.05'
```
![high rotational error](etc/img/high_rot_error.png?raw=true "high rotational error")
high rotational error
