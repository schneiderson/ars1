''' ROBOT MODULE '''
import numpy as np
import pygame
import math
from datetime import datetime
from bot import robot as bot
from bot import genetic as gen
from bot import ann as ann
from bot import beacon as bc
from bot import trigonometry as tri
import time
import queue
import matplotlib.patches as matches
import matplotlib.pyplot as plt

__author__ = 'Steffen Schneider, Camiel Kerkhofs, Olve Dragesat'

pygame.font.init()
game_font = pygame.font.SysFont('arial', 20)
BLACK = (0, 0, 0)
GRAY = (244, 245, 247)
WHITE = (255, 255, 255)
BLUE = (66, 134, 244)
RED = (226, 123, 120)
GREEN = (34, 139, 34)
ORANGE = (255, 165, 0)

DRAW_KALMAN_HISTORY = True

class Environment:
    """
        The environment controls a single simulation at once (graphics are optional)
    """

    def reset(self):
        """
            Reset the environment before a new simulation starts
        """
        self._running = True
        self._paused = False
        self._display_surf = None
        self.graphics_enabled = True
        self.static_time_mode = False
        self.time_dilation = 1

        # reset bot
        self.robot.reset()
        self.neural_net = None
        self.activations = []
        self.rotation_speeds = []
        self.fitness_id = 1
        self.delta_kalman = []
        self.delta_odometry = []
        self.delta_beacon = []

        # Reset the dust grid
        self.cleaned = 0
        self.dirt_sensor = 0
        for index in range(self.grid_size):
            row = [0] * self.grid_size
            self.dirt[index] = row

        self.frames = 0
        self.updates = 0
        self.time = 0                                   # elapsed time in milliseconds
        self.simulation_start_time = datetime.now()     # timestamp

    def __init__(self):
        self._pygame_initialized = False
        self._running = True
        self._paused = False
        self._display_surf = None
        self.graphics_enabled = True
        self.static_time_mode = False
        self.time_dilation = 1

        self.robot = bot.Robot()
        self.neural_net = None
        self.qsize = 10
        self.q = queue.Queue(maxsize=self.qsize)  # Queue of last 10 KF predictions that should be drawn in pygame

        self.velocity_base = 0.1
        self.velocity_min = -1
        self.velocity_max = 1
        
        self.delta_kalman = []
        self.delta_odometry = []
        self.delta_beacon = []

        # Walls
        # A wall is defined as 2 points: [(x1,y1), (x2,y2)] which gives a line from x1,y1 to x2,y2
        self.walls = [
            # Outer walls
            [(50, 50), (750, 50)],
            [(50, 750), (750, 750)],
            [(50, 50), (50, 750)],
            [(750, 50), (750, 750)],

            # Maze walls
            [(200, 150), (650, 300)],
            [(200, 600), (500, 400)],
            # [(300, 300), (300, 500)],
            # [(500, 300), (500, 500)],

            # Inner walls big
            # [(300, 300), (500, 300)],
            # [(300, 500), (500, 500)],
            # [(300, 300), (300, 500)],
            # [(500, 300), (500, 500)],

            # Inner small walls 1
            # [(200, 300), (300, 300)],
            # [(200, 500), (300, 500)],
            # [(200, 300), (200, 500)],
            # [(300, 300), (300, 500)],

            # Inner small walls 2
            # [(400, 300), (500, 300)],
            # [(400, 500), (500, 500)],
            # [(400, 300), (400, 500)],
            # [(500, 300), (500, 500)],

        ]

        # Beacons
        # A beacon is placed at each wallcorner and is reperesented by an x and y coordinate [x, y]
        self.beacons = [
            bc.Beacon(50, 50),
            bc.Beacon(750, 50),
            bc.Beacon(50, 750),
            bc.Beacon(750, 750),

            # Maze walls
            bc.Beacon(200, 150),
            bc.Beacon(650, 300),
            bc.Beacon(200, 600),
            bc.Beacon(500, 400)

            # Inner walls big
            # bc.Beacon(300, 300),
            # bc.Beacon(300, 500),
            # bc.Beacon(500, 300),
            # bc.Beacon(500, 500)
        ]

        # Dust grid (a grid of integers representing the places cleaned by the robot)
        # cell value 0 means the robot has not been there yet (dirty)
        # cell value 1 means the robot has not been there (clean)
        self.grid_size = 128
        self.cleaned = 0
        self.dirt_sensor = 0
        self.dirt = [0] * self.grid_size
        for index in range(self.grid_size):
            row = [0] * self.grid_size
            self.dirt[index] = row

        # Track fitness
        self.activations = []
        self.rotation_speeds = []
        self.fitness_id = 1

        # Display parameters
        self.size = self.width, self.height = 1024, 768
        self.frames = 0
        self.updates = 0
        self.time = 0
        self.simulation_start_time = datetime.now()
        self.delta_t = 0  # Simulation will update using this delta_t if static_time_mode is enabled.

    def on_init(self):
        """
            Initialize the simulation
        """
        if self.graphics_enabled:
            if not self._pygame_initialized:
                pygame.init()
                self._pygame_initialized = True
            self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.robot.update_sensors(self.walls)
        # self.robot.update_beacons(self.beacons, self.walls)
        self.on_render()

    def on_event(self, event):
        """
            Some keyboard events for testing purposes (not used during training)
        """

        if event.type == pygame.QUIT:
            self._running = False
            quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                ## PAUSE
                if self._paused:

                    # Transpose the error matrices to plot more easily
                    beacon_error = np.transpose(self.delta_beacon)
                    kalman_error = np.transpose(self.delta_kalman)
                    odometry_error = np.transpose(self.delta_odometry)

                    # Find out how many measurements
                    x = np.linspace(1, len(beacon_error[0]), len(beacon_error[0]))

                    fig1 = plt.figure()
                    # Plot the X errors

                    plt.subplot(3, 1, 1)
                    plt.plot(x, beacon_error[0], '-', x, kalman_error[0], '-', x, odometry_error[0], '-', linewidth=2)
                    plt.ylabel('X-coordinate')
                    plt.title("Deviation from actual pose")

                    # Plot the Y errors
                    plt.subplot(3, 1, 2)
                    plt.plot(x, beacon_error[1], '-', x, kalman_error[1], '-', x, odometry_error[1], '-', linewidth=2)
                    plt.ylabel('Y-coordinate')

                    # Plot the angle errors
                    plt.subplot(3, 1, 3)
                    l1, l2, l3 = plt.plot(x, beacon_error[2], '-', x, kalman_error[2], '-', x, odometry_error[2], '-', linewidth=2)
                    plt.xlabel('number of elements')
                    plt.ylabel('Angle (degrees)')
                    plt.figlegend((l1, l2, l3), ('sensor', 'kalman filter', 'odometry'))

                    plt.show()
                    self._paused = False

                else:
                    self._paused = True
            if event.key == pygame.K_LEFT:
                self.robot.vel_left += self.velocity_base
            if event.key == pygame.K_RIGHT:
                self.robot.vel_left -= self.velocity_base
            if event.key == pygame.K_UP:
                self.robot.vel_right += self.velocity_base
            if event.key == pygame.K_DOWN:
                self.robot.vel_right -= self.velocity_base

            if self.robot.vel_left > self.velocity_max: self.robot.vel_left = self.velocity_max
            if self.robot.vel_right > self.velocity_max: self.robot.vel_right = self.velocity_max
            if self.robot.vel_left < self.velocity_min: self.robot.vel_left = self.velocity_min
            if self.robot.vel_right < self.velocity_min: self.robot.vel_right = self.velocity_min

    def on_loop(self):
        """
            Update all relevant movement and simulation logic
        """

        # Check update timings
        current_time = self.get_elapsed_time()
        time_since_update = current_time - self.time

        # Wait if time dilation is used
        delta_t = self.delta_t
        if self.delta_t == 0:
            delta_t = time_since_update
        if not self.static_time_mode:
            while time_since_update < self.delta_t:
                time.sleep(0.01)  # wait for 10 ms
                current_time = self.get_elapsed_time()
                time_since_update = current_time - self.time

        self.updates += 1
        self.time = current_time

        # Get a new move from the neural net if it was initialized
        if self.neural_net is not None:
            inputs = []
            for index, sensor in enumerate(self.robot.sensors):
                inputs.append(sensor[1])
            inputs.append(self.dirt_sensor)  # dirt sensor "weighs" the dirt cleaned since last update
            vel_lr = self.neural_net.get_velocities(inputs)
            self.robot.set_velocity(vel_lr[0], vel_lr[1])
            self.rotation_speeds.append(vel_lr)

        # Update robot position
        self.robot.move_robot(delta_t, self.beacons, self.walls)

        # get deviations for plotting
        if( len(self.delta_kalman) < 1000): 
            self.delta_kalman.append(self.robot.get_kf_deviation())
            avg_xy = ( np.sum([x[0] for x in self.delta_kalman]) / len(self.delta_kalman) + np.sum([x[1] for x in self.delta_kalman]) / len(self.delta_kalman) ) / 2
            avg_angle = np.sum([x[2] for x in self.delta_kalman]) / len(self.delta_kalman)
            print("----------------")
            print("kalman avg_xy deviation: ", avg_xy)
            print("kalman avg_angle deviation: ", avg_angle)
        if( len(self.delta_odometry) < 1000): 
            self.delta_odometry.append(self.robot.get_odometry_deviation())
            avg_xy = ( np.sum([x[0] for x in self.delta_odometry]) / len(self.delta_odometry) + np.sum([x[1] for x in self.delta_odometry]) / len(self.delta_odometry) ) / 2
            avg_angle = np.sum([x[2] for x in self.delta_odometry]) / len(self.delta_odometry)
            print("odometry avg_xy deviation: ", avg_xy)
            print("odometry avg_angle deviation: ", avg_angle)
        if( len(self.delta_beacon) < 1000): 
            self.delta_beacon.append(self.robot.get_beacon_deviation())
            avg_xy = ( np.sum([x[0] for x in self.delta_beacon]) / len(self.delta_beacon) + np.sum([x[1] for x in self.delta_beacon]) / len(self.delta_beacon) ) / 2
            avg_angle = np.sum([x[2] for x in self.delta_beacon]) / len(self.delta_beacon)
            print("beacon avg_xy deviation: ", avg_xy)
            print("beacon avg_angle deviation: ", avg_angle)

        # Update robot sensors
        closest_activation = self.robot.update_sensors(self.walls)
        max_activation = self.robot.max_activation
        norm = closest_activation / max_activation
        self.activations.append(norm)

        dirt_value = 5 * norm
        self.dirt_sensor = 0
        # Update dirt
        dirt_i = int(self.robot.posx / (self.width / self.grid_size))
        dirt_j = int(self.robot.posy / (self.height / self.grid_size))
        for n in range(int(math.floor(self.robot.radius / (self.height / self.grid_size))) - 1):
            for m in range(int(math.ceil(self.robot.radius / (self.width / self.grid_size))) - 1):
                if self.dirt[dirt_j - n][dirt_i - m] == 0:
                    self.dirt[dirt_j - n][dirt_i - m] = dirt_value
                    self.dirt_sensor += dirt_value
                if self.dirt[dirt_j + n][dirt_i + m] == 0:
                    self.dirt[dirt_j + n][dirt_i + m] = dirt_value
                    self.dirt_sensor += dirt_value
                if self.dirt[dirt_j - n][dirt_i + m] == 0:
                    self.dirt[dirt_j - n][dirt_i + m] = dirt_value
                    self.dirt_sensor += dirt_value
                if self.dirt[dirt_j + n][dirt_i - m] == 0:
                    self.dirt[dirt_j + n][dirt_i - m] = dirt_value
                    self.dirt_sensor += dirt_value
        self.cleaned += self.dirt_sensor

    def on_render(self):
        """
            print debug information and render the graphics if they are enabled
        """

        if not self.graphics_enabled:
            return True

        self.frames += 1

        debug = self.get_debug_output()
        
        # Clean display
        self._display_surf.fill(GRAY)

        # Draw dirt
        for index_row, dirt_row in enumerate(self.dirt):
            tile_height = self.height / self.grid_size
            y_offset = tile_height * index_row
            for index_column, dirt_column in enumerate(dirt_row):
                if dirt_column > 0:
                    tile_width = self.width / self.grid_size
                    x_offset = tile_width * index_column
                    pygame.draw.rect(self._display_surf, WHITE, (x_offset, y_offset, tile_width, tile_height), 0)

        # Draw walls
        for w in self.walls:
            pygame.draw.line(self._display_surf, BLACK, w[0], w[1])

        # Draw beacons
        for b in self.beacons:
            pygame.draw.circle(self._display_surf, RED, (b.x, b.y), 5, 0)

        # Draw beacon connections
        # robot_pos = (int(self.robot.posx), int(self.robot.posy))
        # for index, beacon in enumerate(self.robot.connected_beacons):
        #     pygame.draw.line(self._display_surf, RED, robot_pos, [beacon.x, beacon.y])

        # Draw sensors
        robot_pos = (int(self.robot.posx), int(self.robot.posy))
        # for index, sensor in enumerate(self.robot.sensors):
        #     pygame.draw.line(self._display_surf, RED, robot_pos, sensor[2])
        #     textsurface = game_font.render(str(index) + ": " + "{0:.0f}".format(sensor[1]), False, RED)
        #     self._display_surf.blit(textsurface, sensor[2])

        # Draw the robot
        pygame.draw.circle(self._display_surf, BLUE, robot_pos, self.robot.radius, 0)
        robot_head = tri.line_endpoint(robot_pos, self.robot.angle, self.robot.radius)
        pygame.draw.line(self._display_surf, BLACK, robot_pos, robot_head, 2)

        # Draw beacon triangulation output
        X_beacons = self.robot.get_robot_beacon_position()
        pygame.draw.circle(self._display_surf, ORANGE, (int(X_beacons[0]), int(X_beacons[1])), 15, 7)
        robot_head = tri.line_endpoint((int(X_beacons[0]), int(X_beacons[1])), X_beacons[2], 15)
        pygame.draw.line(self._display_surf, BLACK, (int(X_beacons[0]), int(X_beacons[1])), robot_head, 2)

        # Draw odometry measurement
        X_odometry = self.robot.get_robot_od_position()
        if X_odometry[0] is not None:
            pygame.draw.circle(self._display_surf, RED, (int(X_odometry[0]), int(X_odometry[1])), 15, 7)
            robot_head = tri.line_endpoint((int(X_odometry[0]), int(X_odometry[1])), X_odometry[2], 15)
            pygame.draw.line(self._display_surf, BLACK,  (int(X_odometry[0]), int(X_odometry[1])), robot_head, 2)

        # Draw Kalman output(s)
        X_believe = self.robot.get_robot_bel_position()
        # remove last item from queue if its longer than max, put new prediction in a queue
        if self.q.full():
            self.q.get()
        self.q.put(X_believe)
        # for each item in self.q, draw to pygame
        for i in range(0, self.qsize):
            belief = self.q.get()
            if i == self.qsize-1 or DRAW_KALMAN_HISTORY:
                pygame.draw.circle(self._display_surf, GREEN, (int(belief[0]), int(belief[1])), 15, 7)
                robot_head = tri.line_endpoint((int(belief[0]), int(belief[1])), belief[2], 15)
                pygame.draw.line(self._display_surf, BLACK, (int(belief[0]), int(belief[1])), robot_head, 2)
            self.q.put(belief)

        # Draw debug metrics
        for index, info in enumerate(debug):
            self._display_surf.blit(game_font.render(info, False, BLACK), (830, 50 + (index * 18)))

        # Kalman info
        types = [(BLUE, 'Actual position', 0), (ORANGE, 'Beacon position', 7), (RED, 'Odometry position', 7), (GREEN, 'Kalman position', 0)]
        pos = [830, 550]
        for t in types:
            pygame.draw.circle(self._display_surf, t[0], pos, int(self.robot.radius/2), t[2])
            self._display_surf.blit(game_font.render(t[1], False, BLACK), (pos[0]+40, pos[1]-15))
            pos[1] += int(self.robot.radius)+10

        # Update display
        pygame.display.update()

    def get_debug_output(self):
        return ["Debug info:",
                 "Realtime: " + str(int(self.get_elapsed_time(realtime=True) / 1000)) + " s",
                 "Simulation time: " + str(int(self.get_elapsed_time() / 1000)) + " s",
                 "Time dilation: * " + str(self.time_dilation),
                 "Frames: " + str(self.frames),
                 "FPS: " + str(int(self.frames / max(1, (self.get_elapsed_time(realtime=True) / 1000)))),
                 "Updates: " + str(self.updates),
                 "UPS: " + str(int(self.updates / max(1, (self.get_elapsed_time(realtime=True) / 1000)))),
                 "",
                 "Robot:",
                 "  Angle: " + str(int(self.robot.angle)),
                 "  Pos_x: " + str(int(self.robot.posx)),
                 "  Pos_y: " + str(int(self.robot.posy)),
                 "  Vel_left: " + str(float(format(self.robot.vel_left, '.2f'))),
                 "  Vel_right: " + str(float(format(self.robot.vel_right, '.2f'))),
                 "",
                 "Fitness:",
                 "  Cleaned: " + str(int(self.cleaned)),
                 "  Collisions: " + str(self.robot.num_collisions),
                 "  Activations: " + str(len(self.activations)),
                 "  Evaluation: " + str(int(self.fitness())),
                 "",
                 "",
                 # "Genetic algorithm: ",
                 # "   Current generation: ",
                 # "      Gen number: " + str(gen.GenAlg.generation_counter),
                 # "      Size: " + str(gen.GenAlg.pop_size_current),
                 # "      Progress: " + str(gen.GenAlg.gen_progress) + "/" + str(gen.GenAlg.pop_size_current),
                 # "   Last generation: ",
                 # "      Gen number: " + str(gen.GenAlg.generation_counter - 1),
                 # "      Best cost: " + str(gen.GenAlg.best_cost),
                 # "      Avg cost: " + str(gen.GenAlg.avg_cost),
                 "HIT SPACE TO PAUSE"]

    def get_elapsed_time(self, realtime=False):
        """
            Returns the elapsed time in milliseconds multiplied by the time dilation factor
            If realtime is set to True, time dilation is ignored
        """
        # Returns a fake elapsed time if time mode is static
        if self.static_time_mode and not realtime:
            return int(self.delta_t * self.updates)

        # Calculate the actual elapsed time
        elapsed_t = self.time_diff_ms(datetime.now(), self.simulation_start_time)
        if realtime:
            return int(elapsed_t)
        else:
            return int(elapsed_t * self.time_dilation)

    def simulate(self, graphics_enabled=True, time_dilation=1, timeout=0, weights=[], static_delta_t=None, recurrence=False, start_x=0, start_y=0, start_angle=0, fitness_id=1):
        """
            Start a simulation
            graphics_enabled: boolean; If set to false, graphics rendering is skipped
            time_dilation: integer; All time interactions are multiplied  by this factor. 1 = realtime
                Set time_dilation to 0 to use a static delta_t for updating (simulation will run as fast as hardware allows)
            timeout: integer; Timeout of simulation in seconds. 0 = no timeout

            Returns the fitness evaluation of the simulation (float) when the simulation is finished
        """
        try:
            self.reset()
            # Apply configuration parameters and check their validity
            self.graphics_enabled = graphics_enabled
            self.fitness_id = fitness_id
            if len(weights) > 0:
                self.neural_net = ann.NeuralNet(weights, recurrence=recurrence)
            else:
                # Just use some sample velocity in case weights are missing (demo mode)
                self.robot.set_velocity(0.65, 0.5)  # 0.65,0.5 = circle movement
                # self.robot.set_velocity(1, 1)
            self.time_dilation = time_dilation
            if time_dilation == 0:
                self.static_time_mode = True
            if static_delta_t is not None:
                # Static delta_t can not exceed the robots radius or else it will shoot trough environment limits!
                if static_delta_t > 200:
                    raise ValueError('delta_t exceeds the limit of 200ms. Requested delta_t: ' + str(static_delta_t))
                self.delta_t = static_delta_t
            else:
                if time_dilation == 0:
                    self.delta_t = 200

            if start_x != 0 and start_y != 0:
                self.robot.set_robot_initial_position(start_x, start_y, start_angle)

            if self.on_init() == False:
                # Has no return value but will return False if pygame library encounters an internal error
                raise ValueError('Error during pygame initialization')

            # Reset simulation time
            self.time = 0
            self.simulation_start_time = datetime.now()

            while self._running:
                if graphics_enabled:
                    for event in pygame.event.get():
                        self.on_event(event)
                if not self._paused:
                    self.on_loop()
                    self.on_render()

                if timeout > 0:
                    if (self.get_elapsed_time() > (timeout * 1000)):
                        self._running = False

            #pygame.quit()


            return self.fitness()
        except IndexError as inst:
            print('\033[91m' + "=== INDEX ERROR === Simulation failed with message: ")
            print(inst)
            if self.static_time_mode:
                print("This error is likely caused by the robot going off screen. Try lowering the static delta_time")
            else:
                print("This error is likely caused by the robot going off screen. Try lowering the time dilation")
            print('\033[0m' + "\n")
            return 0
        # except Exception as inst:
        #     print('\033[91m' + "=== ERROR === Simulation failed with message: ")
        #     print(inst)
        #     print('\033[0m' + "\n")
        #     return 0

    def fitness(self):
        """
            Returns the current fitness evaluation of the simulation (float)
        """

        if self.fitness_id == 1:
            # 1: Simple fitness: total number of dust collected
            return self.cleaned


        elif self.fitness_id == 2:
            # 2: Total number of dust collected devided by the number of collisions
            return self.cleaned / (1+self.robot.num_collisions * 0.3)


        elif self.fitness_id == 3 and len(self.activations) > 0:
            # 3: Total number of dust collected * sensor activation / num collisions
            total = 0
            for i in self.activations:
                total += i
            avg = total / len(self.activations)
            return (self.cleaned * avg) / (1+(self.robot.num_collisions * 0.3))


        elif self.fitness_id == 4 and len(self.activations) > 0 and len(self.activations) == len(self.rotation_speeds):
            # 4: Wheel speeds + activation (from slides)
            # self.activations and self.rotation_speeds contain the values at each update
            fitness = 0

            for n in range(len(self.activations)):
                # Normalized activation value
                i = self.activations[n]

                # Average of unsigned velocities for both wheels
                v = (abs(self.rotation_speeds[n][0]) + abs(self.rotation_speeds[n][1])) / 2

                # Absolute algebraic difference
                delta_v = abs(self.rotation_speeds[n][0]-self.rotation_speeds[n][1])

                evaluate = (v*(1-math.sqrt(delta_v)))*(1-i)
                fitness += evaluate

            return fitness


        elif self.fitness_id == 5 and len(self.activations) > 0 and len(self.activations) == len(self.rotation_speeds):
            # 5: Wheel speeds + activation (from slides)
            # self.activations and self.rotation_speeds contain the values at each update
            fitness = 0

            for n in range(len(self.activations)):
                # Normalized activation value
                i = self.activations[n]

                # Average of unsigned velocities for both wheels
                v = (abs(self.rotation_speeds[n][0]) + abs(self.rotation_speeds[n][1])) / 2

                # Absolute algebraic difference
                delta_v = abs(self.rotation_speeds[n][0]-self.rotation_speeds[n][1])

                evaluate = (v*(1-math.sqrt(delta_v)))*(1-i)
                fitness += evaluate

            return self.cleaned / fitness
        else:
            return 0

    def time_diff_ms(self, time1, time2):
        dt = time1 - time2
        ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
        return ms
