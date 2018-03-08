''' ROBOT MODULE '''
import pygame
import math
from bot import robot as bot
from bot import ann as ann

__author__ = 'Steffen Schneider, Camiel Kerkhofs'

pygame.font.init()
game_font = pygame.font.SysFont('arial', 16)
BLACK = (0, 0, 0)
GRAY = (244, 245, 247)
WHITE = (255, 255, 255)
BLUE = (66, 134, 244)
RED = (226, 123, 120)

class Environment:
    """
        The environment controls a single simulation (graphics are optional)
    """

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.graphics_enabled = True
        self.time_dilation = 1  # Time dilation can be used to speed up or slow down simulation. All time interactions are multiplied by this factor. 1 = realtime

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

        # Dirt (a grid of integers representing the places cleaned by the robot)
        # cell value 0 means the robot has not been there yet (dirty)
        # cell value 1 means the robot has not been there (clean)
        self.grid_size = 128  # Very resource intensive when graphics are enabled! keep low when running with graphics and turn up during simulation
        self.cleaned = 0
        self.dirt = [0] * self.grid_size
        for index in range(self.grid_size):
            row = [0] * self.grid_size
            self.dirt[index] = row

        # Display parameters
        self.size = self.width, self.height = 1024, 768
        self.frames = 0
        self.updates = 0
        self.time = self.get_elapsed_time()

    def on_init(self):
        """
            Initialize the simulation
        """

        pygame.init()
        if self.graphics_enabled: self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.robot.update_sensors(self.walls)
        self.on_render()

    def on_event(self, event):
        """
            Some keyboard events for testing purposes (not used during training)
        """

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

        # Calculate time since last frame
        current_time = self.get_elapsed_time()
        delta_time = current_time - self.time

        if delta_time - 10 > 0:
            self.updates += 1
            self.time = current_time

            # Get a new move from the neural net if it was initialized
            if self.neural_net is not None:
                inputs = [] * len(self.robot.sensors)
                for index, sensor in enumerate(self.robot.sensors):
                    inputs[index] = sensor[1]
                vel_lr = self.neural_net.get_velocities(inputs)
                self.robot.set_velocity(vel_lr[0], vel_lr[1])

            # Update robot position
            self.robot.move_robot(delta_time)

            # Update robot sensors
            self.robot.update_sensors(self.walls)

            # Update dirt
            dirt_i = int(self.robot.posx / (self.width / self.grid_size))
            dirt_j = int(self.robot.posy / (self.height / self.grid_size))
            for n in range(int(math.floor(self.robot.radius / (self.height / self.grid_size))) - 1):
                for m in range(int(math.ceil(self.robot.radius / (self.width / self.grid_size))) - 1):
                    if self.dirt[dirt_j - n][dirt_i - m] == 0:
                        self.dirt[dirt_j - n][dirt_i - m] = 1
                        self.cleaned += 1
                    if self.dirt[dirt_j + n][dirt_i + m] == 0:
                        self.dirt[dirt_j + n][dirt_i + m] = 1
                        self.cleaned += 1
                    if self.dirt[dirt_j - n][dirt_i + m] == 0:
                        self.dirt[dirt_j - n][dirt_i + m] = 1
                        self.cleaned += 1
                    if self.dirt[dirt_j + n][dirt_i - m] == 0:
                        self.dirt[dirt_j + n][dirt_i - m] = 1
                        self.cleaned += 1

    def on_render(self):
        """
            print debug information and render the graphics if they are enabled
        """

        self.frames += 1

        debug = ["Debug info:",
                 "Realtime: " + str(pygame.time.get_ticks()) + " ms",
                 "Simulation time: " + str(self.get_elapsed_time()) + " ms",
                 "Time dilation: * " + str(self.time_dilation),
                 "Frames: " + str(self.frames),
                 "FPS: " + str(self.frames / (pygame.time.get_ticks() / 1000)),
                 "Updates: " + str(self.updates),
                 "UPS: " + str(self.updates / (pygame.time.get_ticks() / 1000)),
                 "",
                 "Robot:",
                 "Angle: " + str(self.robot.angle),
                 "Pos_x: " + str(self.robot.posx),
                 "Pos_y: " + str(self.robot.posy),
                 "Vel_left: " + str(self.robot.vel_left),
                 "Vel_right: " + str(self.robot.vel_right),
                 "",
                 "Cleaned: " + str(self.cleaned)]
        if not self.graphics_enabled:
            if self.get_elapsed_time() % (1000 * self.time_dilation) == 0:
                print("\n" * 10)
                for index, info in enumerate(debug):
                    print(info)
        else:
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

    def get_elapsed_time(self):
        """
            Returns the elapsed pygame time multiplied by the time dilation factor
        """

        return int(pygame.time.get_ticks() * self.time_dilation)

    def simulate(self, graphics_enabled=True, time_dilation=1, timeout=0, weights=[]):
        """
            Start a simulation
            graphics_enabled: boolean; If set to false, graphics rendering is skipped
            time_dilation: integer; All time interactions are multiplied  by this factor. 1 = realtime
            timeout: integer; Timeout of simulation in seconds. 0 = no timeout

            Returns the fitness evaluation of the simulation (float) when the simluation is finished
        """

        try:
            # Apply configuration parameters
            self.time_dilation = time_dilation
            self.graphics_enabled = graphics_enabled
            if len(weights) > 0:
                self.neural_net = ann.ANN(weights)
            else:
                # Just use some sample velocity in case weights are missing
                self.robot.set_velocity(0.65, 0.5)

            if self.on_init() == False:
                self._running = False

            start_time = self.get_elapsed_time()
            while self._running:
                if graphics_enabled:
                    for event in pygame.event.get():
                        self.on_event(event)
                self.on_loop()
                self.on_render()

                if timeout > 0:
                    if self.get_elapsed_time() - (timeout * 1000) > start_time:
                        self._running = False

            pygame.quit()
            return self.fitness()
        except Exception as inst:
            print('\033[91m' + "=== ERROR === Simulation failed with message: ")
            print(inst)
            print('\033[0m' + "\n")
            return 0

    def fitness(self):
        """
            Returns the current fitness evaluation of the simulation (float)
        """

        # TODO: Test different fitness functions
        return self.cleaned
