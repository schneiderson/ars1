''' ROBOT MODULE '''
import pygame
import math
from datetime import datetime
from bot import robot as bot
from bot import genetic as gen
from bot import ann as ann

__author__ = 'Steffen Schneider, Camiel Kerkhofs, Olve Dragesat'

pygame.font.init()
game_font = pygame.font.SysFont('arial', 16)
BLACK = (0, 0, 0)
GRAY = (244, 245, 247)
WHITE = (255, 255, 255)
BLUE = (66, 134, 244)
RED = (226, 123, 120)


class Environment:
    """
        The environment controls a single simulation at once (graphics are optional)
    """

    def reset(self):
        """
            Reset the environment before a new simulation starts
        """
        self._running = True
        self._display_surf = None
        self.graphics_enabled = True
        self.static_time_mode = False
        self.time_dilation = 1

        # reset bot
        self.robot.reset()
        self.neural_net = None

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
        self._display_surf = None
        self.graphics_enabled = True
        self.static_time_mode = False
        self.time_dilation = 1

        self.robot = bot.Robot()
        self.neural_net = None

        self.velocity_base = 0.1
        self.velocity_min = -1
        self.velocity_max = 1

        # Walls
        # A wall is defined as 2 points: [(x1,y1), (x2,y2)] which gives a line from x1,y1 to x2,y2
        self.walls = [
            # Outer walls
            [(50, 50), (750, 50)],
            [(50, 750), (750, 750)],
            [(50, 50), (50, 750)],
            [(750, 50), (750, 750)],

            # Inner walls
            [(300, 300), (500, 300)],
            [(300, 500), (500, 500)],
            [(300, 300), (300, 500)],
            [(500, 300), (500, 500)],

        ]

        # Dust grid (a grid of integers representing the places cleaned by the robot)
        # cell value 0 means the robot has not been there yet (dirty)
        # cell value 1 means the robot has not been there (clean)
        self.grid_size = 128  # Very resource intensive when graphics are enabled! keep low when running with graphics and turn up during simulation
        self.cleaned = 0
        self.dirt_sensor = 0
        self.dirt = [0] * self.grid_size
        for index in range(self.grid_size):
            row = [0] * self.grid_size
            self.dirt[index] = row

        # Display parameters
        self.size = self.width, self.height = 1024, 768
        self.frames = 0
        self.updates = 0
        self.time = 0
        self.simulation_start_time = datetime.now()
        self.static_time_mode_delta_t = 200  # Simulation will update using this delta_t if static_time_mode is enabled.

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
        self.on_render()

    def on_event(self, event):
        """
            Some keyboard events for testing purposes (not used during training)
        """

        if not self.graphics_enabled:
            return True

        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYUP:
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

        # Check if update is allowed (always allowed if static time mode is enabled)
        update = False
        if self.static_time_mode:
            # Use the static delta t
            update = True
            delta_time = self.static_time_mode_delta_t
        else:
            # Calculate time since last frame
            current_time = self.get_elapsed_time()
            delta_time = current_time - self.time
            if delta_time - 10 > 0:
                update = True
                self.time = current_time

        if update:
            self.updates += 1

            # Get a new move from the neural net if it was initialized
            if self.neural_net is not None:
                inputs = []
                for index, sensor in enumerate(self.robot.sensors):
                    inputs.append(sensor[1])
                inputs.append(self.dirt_sensor)  # dirt sensor "weighs" the dirt cleaned since last update
                vel_lr = self.neural_net.get_velocities(inputs)
                self.robot.set_velocity(vel_lr[0], vel_lr[1])

            # Update robot position
            self.robot.move_robot(delta_time)

            # Update robot sensors
            self.robot.update_sensors(self.walls)

            self.dirt_sensor = 0
            # Update dirt
            dirt_i = int(self.robot.posx / (self.width / self.grid_size))
            dirt_j = int(self.robot.posy / (self.height / self.grid_size))
            for n in range(int(math.floor(self.robot.radius / (self.height / self.grid_size))) - 1):
                for m in range(int(math.ceil(self.robot.radius / (self.width / self.grid_size))) - 1):
                    if self.dirt[dirt_j - n][dirt_i - m] == 0:
                        self.dirt[dirt_j - n][dirt_i - m] = 1
                        self.dirt_sensor += 1
                    if self.dirt[dirt_j + n][dirt_i + m] == 0:
                        self.dirt[dirt_j + n][dirt_i + m] = 1
                        self.dirt_sensor += 1
                    if self.dirt[dirt_j - n][dirt_i + m] == 0:
                        self.dirt[dirt_j - n][dirt_i + m] = 1
                        self.dirt_sensor += 1
                    if self.dirt[dirt_j + n][dirt_i - m] == 0:
                        self.dirt[dirt_j + n][dirt_i - m] = 1
                        self.dirt_sensor += 1
            self.cleaned += self.dirt_sensor

    def on_render(self):
        """
            print debug information and render the graphics if they are enabled
        """

        if not self.graphics_enabled:
            return True

        self.frames += 1

        debug = ["Debug info:",
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
                 "  Cleaned: " + str(self.cleaned),
                 "  Collisions: " + str(self.robot.num_collisions),
                 "  Evaluation: " + str(self.fitness()),
                 "",
                 "Genetic algorithm: ",
                 "   Current generation: ",
                 "      Gen number: " + str(gen.GenAlg.generation_counter),
                 "      Size: " + str(gen.GenAlg.pop_size_current),
                 "      Progress: " + str(gen.GenAlg.gen_progress) + "/" + str(gen.GenAlg.pop_size_current),
                 "   Last generation: ",
                 "      Gen number: " + str(gen.GenAlg.generation_counter - 1),
                 "      Best cost: " + str(gen.GenAlg.best_cost),
                 "      Avg cost: " + str(gen.GenAlg.avg_cost),
                 ""]
        # if not self.graphics_enabled:
        #     # Prints the debug information to the console every 2 seconds (realtime)
        #     if self.get_elapsed_time(realtime=True) % 2000 == 0:
        #         print("\n" * 10)
        #         for index, info in enumerate(debug):
        #             print(info)
        # else:
            # Clean display
            self._display_surf.fill(GRAY)

            # Draw dirt
            for index_row, dirt_row in enumerate(self.dirt):
                tile_height = self.height / self.grid_size
                y_offset = tile_height * index_row
                for index_column, dirt_column in enumerate(dirt_row):
                    if dirt_column == 1:
                        tile_width = self.width / self.grid_size
                        x_offset = tile_width * index_column
                        pygame.draw.rect(self._display_surf, WHITE, (x_offset, y_offset, tile_width, tile_height), 0)

            # Draw walls
            for w in self.walls:
                pygame.draw.line(self._display_surf, BLACK, w[0], w[1])

            # Draw sensors
            robot_pos = (int(self.robot.posx), int(self.robot.posy))
            for index, sensor in enumerate(self.robot.sensors):
                pygame.draw.line(self._display_surf, RED, robot_pos, sensor[2])
                textsurface = game_font.render(str(index) + ": " + "{0:.0f}".format(sensor[1]), False, RED)
                self._display_surf.blit(textsurface, sensor[2])

            # Draw the robot
            pygame.draw.circle(self._display_surf, BLUE, robot_pos, self.robot.radius, 0)
            theta_rad = math.radians(self.robot.angle)
            robot_head = \
                self.robot.posx + self.robot.radius * math.cos(theta_rad), \
                self.robot.posy + self.robot.radius * math.sin(theta_rad)
            pygame.draw.line(self._display_surf, BLACK, robot_pos, robot_head, 2)

            # Draw debug metrics
            for index, info in enumerate(debug):
                self._display_surf.blit(game_font.render(info, False, BLACK), (800, 50 + (index * 15)))

            # Update display
            pygame.display.update()

    def get_elapsed_time(self, realtime=False):
        """
            Returns the elapsed time in milliseconds multiplied by the time dilation factor
            If realtime is set to True, time dilation is ignored
        """
        # Returns a fake elapsed time if time mode is static
        if self.static_time_mode and not realtime:
            return int(self.static_time_mode_delta_t * self.updates)

        # Calculate the actual elapsed time
        elapsed_t = self.time_diff_ms(datetime.now(), self.simulation_start_time)
        if realtime:
            return int(elapsed_t)
        else:
            return int(elapsed_t * self.time_dilation)

    def simulate(self, graphics_enabled=True, time_dilation=1, timeout=0, weights=[], static_delta_t=None):
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
            if len(weights) > 0:
                self.neural_net = ann.NeuralNet(weights)
            else:
                # Just use some sample velocity in case weights are missing (demo mode)
                # self.robot.set_velocity(0.65, 0.5)  # 0.65,0.5 = circle movement
                self.robot.set_velocity(1, 1)
            self.time_dilation = time_dilation
            if time_dilation == 0:
                self.static_time_mode = True
                if static_delta_t is not None:
                    # Static delta_t can not exceed the robots radius or else it will shoot trough environment limits!
                    if static_delta_t > 200:
                        raise ValueError('delta_t exceeds the limit of 200ms. Requested delta_t: ' + str(static_delta_t))
                    self.static_time_mode_delta_t = static_delta_t

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

        # TODO: Test different fitness functions
        # return self.cleaned  # Basic distance travelled
        return self.cleaned / (1+self.robot.num_collisions) # Basic distance travelled + low num_collisions is rewarded


    def time_diff_ms(self, time1, time2):
        dt = time1 - time2
        ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
        return ms