import pygame
import math
from pygame.locals import *
from bot import kinematics as kin

pygame.font.init()
game_font = pygame.font.SysFont('arial', 16)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (66, 134, 244)
RED = (226, 123, 120)
COLLISION_TOLERANCE = 0.001

class Ars1:
    def __init__(self):
        self._running = True
        self._display_surf = None

        # Robot parameters
        self.robot_radius = 30
        self.posx = 400
        self.posy = 175
        self.robot_angle = 0
        
        self.velocity_base = 0.1
        self.velocity_max = 1
        self.vel_left = 0.65
        self.vel_right = 0.50

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
        
        # Infrared sensors
        # For each sensor we have (A, B, C) where:
        #   - A is the linear distance measure between 0 and sensor_max
        #   - B is the transformed distance measure given by (sensor_max - A) ^ dist_transformation_factor
        #   - C is the position (x,y) of the intersection
        self.sensor_max = 500
        self.dist_transformation_factor = 2
        self.sensors = [(0, 0, (self.posx,self.posy))] * 12

        # Display parameters
        self.size = self.width, self.height = 1000, 800
        self.frames = 0
        self.time = pygame.time.get_ticks()
        
    def update_robot_posx(self, x):
        self.posx = x
        
    def update_robot_posy(self, y):
        self.posy = y

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        self.update_sensors()
        self.redraw()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.vel_left = self.vel_left + self.velocity_base
            if event.key == pygame.K_RIGHT:
                self.vel_left = self.vel_left - self.velocity_base
            if event.key == pygame.K_UP:
                self.vel_right = self.vel_right + self.velocity_base
            if event.key == pygame.K_DOWN:
                self.vel_right = self.vel_right - self.velocity_base
            
            if self.vel_left > self.velocity_max: self.vel_left = self.velocity_max
            if self.vel_right > self.velocity_max: self.vel_right = self.velocity_max
            if self.vel_left < -self.velocity_max: self.vel_left = -self.velocity_max
            if self.vel_right < -self.velocity_max: self.vel_right = -self.velocity_max

        self.redraw()

    def on_loop(self):
        # Update position
        delta_time = pygame.time.get_ticks() - self.time  # Calculate time since last frame
        if delta_time - 20 > 0:
            self.time = pygame.time.get_ticks()
            
            # vel_right and vel_left are switched on purpose to compensate for the pygame coordinate system (y-axis is flipped, with 0,0 point being top left)
            left_velocity = float(format(self.vel_right, '.5f'))
            right_velocity = float(format(self.vel_left, '.5f'))
            pos = kin.bot_calc_coordinate(self.posx, self.posy, self.robot_angle, left_velocity, right_velocity, delta_time/10, self.robot_radius*2)
            self.update_robot_posx(pos[0])
            self.update_robot_posy(pos[1])
            self.robot_angle = pos[2]
                
        # Update sensors
        self.update_sensors()

    def on_render(self):
        self.redraw()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def redraw(self):
        self.frames += 1
        # Clean display
        self._display_surf.fill(WHITE)

        # Draw walls
        for w in self.walls:
            pygame.draw.line(self._display_surf, BLACK, w[0], w[1])
        
        # Draw sensors
        robot_pos = (int(self.posx), int(self.posy))
        for index, sensor in enumerate(self.sensors):
            pygame.draw.line(self._display_surf, RED, robot_pos, sensor[2])
            textsurface = game_font.render(str(index) + ": " + "{0:.0f}".format(sensor[1]), False, RED)
            self._display_surf.blit(textsurface, sensor[2])
            
        # Draw the robot
        pygame.draw.circle(self._display_surf, BLUE, robot_pos, self.robot_radius, 0)
        theta_rad = math.radians(self.robot_angle)
        robot_head = \
            self.posx + self.robot_radius * math.cos(theta_rad), \
            self.posy + self.robot_radius * math.sin(theta_rad)
        pygame.draw.line(self._display_surf, BLACK, robot_pos, robot_head, 2)
            
        # Draw debug metrics
        debug = ["Debug info:",
                 "Time: " + str(pygame.time.get_ticks()) + " ms",
                 "Frames: " + str(self.frames),
                 "FPS: " + str(self.frames / (pygame.time.get_ticks()/1000)),
                 "",
                 "Robot:",
                 "Angle: " + str(self.robot_angle),
                 "Pos_x: " + str(self.posx),
                 "Pos_y: " + str(self.posy),
                 "Vel _left: " + str(self.vel_left),
                 "Vel_right: " + str(self.vel_right)]
        for index, info in enumerate(debug):
            self._display_surf.blit(game_font.render(info, False, BLACK), (800,50+(index*15)))
        
        # Update display
        pygame.display.update()

    # Update all infrared sensor values
    # Author: Camiel Kerkhofs
    def update_sensors(self):
        
        for index, sensor in enumerate(self.sensors):
            # Determine current sensor endpoint
            closest_collision = self.sensor_max
            sensor_angle = ((360 / len(self.sensors)) * index)
            angle = (self.robot_angle + sensor_angle) % 360
            theta_rad = math.radians(angle)
            sensor_end = \
                self.posx + closest_collision * math.cos(theta_rad), \
                self.posy + closest_collision * math.sin(theta_rad)
            intersect_wall = 0

            # Check collision points for each wall
            for wall in self.walls:
                intersect = self.find_line_intersect(wall[0],wall[1],(self.posx, self.posy),sensor_end)

                if intersect:
                    # Determine distance to intersect
                    distance = math.sqrt((intersect[0] - self.posx) ** 2 + (intersect[1] - self.posy) ** 2)
                    if distance < closest_collision:
                        closest_collision = distance
                        sensor_end = intersect
                        intersect_wall = wall
                        
            # Transform linear distance measure and update sensor value
            # TODO: find a distance transformation that fits the ANN
            transformed_distance = (self.sensor_max - closest_collision) ** self.dist_transformation_factor
            self.sensors[index] = [closest_collision, transformed_distance, sensor_end]
            
            # Handle wall collisions, apply motion only parallel to wall, rest motion perpendicular to wall
            if closest_collision < self.robot_radius - COLLISION_TOLERANCE:
                # The robot is moved back along the angle of the current (infringing) sensor using the illegal distance
                illegal_distance = (self.robot_radius - closest_collision) + self.robot_radius
                corrected_position = sensor_end[0] - illegal_distance * math.cos(theta_rad), \
                                     sensor_end[1] - illegal_distance * math.sin(theta_rad)
                self.update_robot_posx(corrected_position[0])
                self.update_robot_posy(corrected_position[1])
                
                self.update_sensors()
                
                # TODO: motion parallel from wall continues normally, but should be slown down by a weight to discourage 'pushing' the wall
                # xDiff = intersect_wall[1][0] - intersect_wall[0][0]
                # yDiff = intersect_wall[1][1] - intersect_wall[0][1]
                # wall_angle = math.degrees(math.atan2(yDiff, xDiff))

    # Finds the intersection between two lines a and b defined by their respective endpoints p1 and p2
    # Author: Camiel Kerkhofs
    def find_line_intersect(self, a_p1, a_p2, b_p1, b_p2):

        # Check if lines intersect
        if a_p1[0] > b_p1[0] and a_p1[0] > b_p2[0] and a_p2[0] > b_p1[0] and a_p2[0] > b_p2[0]: return False
        if a_p1[0] < b_p1[0] and a_p1[0] < b_p2[0] and a_p2[0] < b_p1[0] and a_p2[0] < b_p2[0]: return False
        if a_p1[1] > b_p1[1] and a_p1[1] > b_p2[1] and a_p2[1] > b_p1[1] and a_p2[1] > b_p2[1]: return False
        if a_p1[1] < b_p1[1] and a_p1[1] < b_p2[1] and a_p2[1] < b_p1[1] and a_p2[1] < b_p2[1]: return False

        # Get diffs along each axis
        x_diff = (a_p1[0] - a_p2[0], b_p1[0] - b_p2[0])
        y_diff = (a_p1[1] - a_p2[1], b_p1[1] - b_p2[1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        # Find the intersection
        div = det(x_diff, y_diff)
        if div == 0: return False
        d = (det(* (a_p1,a_p2)), det(* (b_p1,b_p2)))
        x = det(d, x_diff) / div
        y = det(d, y_diff) / div
        
        # Check if intersection exceeds the segments
        if x < min(a_p1[0], a_p2[0]) - COLLISION_TOLERANCE: return False
        if x > max(a_p1[0], a_p2[0]) + COLLISION_TOLERANCE: return False
        if y < min(a_p1[1], a_p2[1]) - COLLISION_TOLERANCE: return False
        if y > max(a_p1[1], a_p2[1]) + COLLISION_TOLERANCE: return False
        if x < min(b_p1[0], b_p2[0]) - COLLISION_TOLERANCE: return False
        if x > max(b_p1[0], b_p2[0]) + COLLISION_TOLERANCE: return False
        if y < min(b_p1[1], b_p2[1]) - COLLISION_TOLERANCE: return False
        if y > max(b_p1[1], b_p2[1]) + COLLISION_TOLERANCE: return False
    
        return x, y

if __name__ == "__main__":
    ars1_app = Ars1()
    ars1_app.on_execute()
