from bot import odometry as od
import matplotlib.pyplot as plt
import argparse

# get cli arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--noise", help='noise weights', action='store')
args = parser.parse_args()

# default noise values
noise = [.01, .02, .02, .02]

# get error parameters
if args.noise:
    noise = [ float(e) for e in args.noise.split(",") ]
print("noise parameters: ", noise )

odometry = od.odometry()

u_t1 = [(0, 0, 0), (2, 0, 0)]
u_t2 = [(2, 0, 0), (4, 0, 0)]
u_t3 = [(4, 0, 0), (6, 0, 0)]
u_t4 = [(6, 0, 0), (8, 0, 0)]
u_t5 = [(8, 0, 0), (10, 0, 0)]

odometry.set_noise_params( noise )
#odometry.set_sample_func( od.sample_triang_dist )

positions = []
for x in range(0, 200):
    pos1 = odometry.sample_motion_model(u_t1, u_t1[0])
    pos2 = odometry.sample_motion_model(u_t2, pos1)
    pos3 = odometry.sample_motion_model(u_t3, pos2)
    pos4 = odometry.sample_motion_model(u_t4, pos3)
    pos5 = odometry.sample_motion_model(u_t5, pos4)
    positions.append(pos1)
    positions.append(pos2)
    positions.append(pos3)
    positions.append(pos4)
    positions.append(pos5)

xs = [x[0] for x in positions]
ys = [x[1] for x in positions]

# plot
plt.scatter(0, 0, c='r')
plt.scatter(xs, ys, c='b', alpha=0.3)
plt.axis([0, 15, -5, 5])
plt.show()