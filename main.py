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

class Ars1:
    def __init__(self):
        self._running = True
        self._display_surf = None

        # Robot parameters
        self.robot_radius = 30
        self.posx = 400
        self.posy = 400
        self.previous_posx = 0
        self.previous_posy = 0
        self.robot_angle = 0
        
        self.velocity_base = 1
        self.velocity_max = 10
        self.vel_left = 6
        self.vel_right = 5

        # Walls
        # A wall is defined as 2 points: [(x1,y1), (x2,y2)] which gives a line from x1,y1 to x2,y2
        self.walls = [
            # Outer walls
            [(50, 50), (750, 50)],
            [(50, 750), (750, 750)],
            [(50, 50), (50, 750)],
            [(750, 50), (750, 750)],
            
            # Inner walls
            # [(300, 300), (500, 300)],
            # [(300, 500), (500, 500)],
            # [(300, 300), (300, 500)],
            # [(500, 300), (500, 500)],
        
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
        self.previous_posx = self.posx
        self.posx = x
        
    def update_robot_posy(self, y):
        self.previous_posy = self.posy
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
        if delta_time - 250 > 0:
            self.time = pygame.time.get_ticks()
            
            # TODO: check coordinate calculation
            pos = kin.bot_calc_coordinate(self.posx, self.posy, self.robot_angle, self.vel_right, self.vel_left, delta_time/100, self.robot_radius)
            self.update_robot_posx(int(pos[0]))
            self.update_robot_posy(int(pos[1]))
            self.robot_angle = int(pos[2])
                
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
        robot_pos = (self.posx, self.posy)
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
                "Vel_left: " + str(self.vel_left),
                "Vel_right: " + str(self.vel_right)]
        for index, info in enumerate(debug):
            self._display_surf.blit(game_font.render(info, False, BLACK), (800,50+(index*15)))
        
        # Update display
        pygame.display.update()

    # Update all infrared sensor values
    # Author: Camiel Kerkhofs
    def update_sensors(self):
        # Skip update if there has been no movement
        # if (self.previous_posx == self.posx and self.previous_posy == self.posy):
        #     return True
        
        for index, sensor in enumerate(self.sensors):
            # Determine current sensor endpoint
            closest_collision = self.sensor_max
            sensor_angle = ((360 / len(self.sensors)) * index)
            angle = (self.robot_angle + sensor_angle) % 360
            theta_rad = math.radians(angle)
            sensor_end = \
                self.posx + closest_collision * math.cos(theta_rad), \
                self.posy + closest_collision * math.sin(theta_rad)

            # Check collision points for each wall
            for wall in self.walls:
                intersect = self.find_line_intersect(wall[0],wall[1],(self.posx, self.posy),sensor_end)

                if intersect:
                    # Determine distance to intersect
                    distance = math.sqrt((intersect[0] - self.posx) ** 2 + (intersect[1] - self.posy) ** 2)
                    if distance < closest_collision:
                        closest_collision = distance
                        sensor_end = intersect
                        
            # Transform linear distance measure and update sensor value
            # TODO: find a distance transformation that fits the ANN
            transformed_distance = (self.sensor_max - closest_collision) ** self.dist_transformation_factor
            self.sensors[index] = [closest_collision, transformed_distance, sensor_end]
            
            # Restore previous position upon collision with wall
            # TODO: properly handle collision event (For collision handling, apply motion only parallel to wall, rest motion perpendicular to wall)
            if closest_collision < self.robot_radius-5:
                self.update_robot_posx(self.previous_posx)
                self.update_robot_posy(self.previous_posy)

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
        TOLERANCE = 0.001
        if x < min(a_p1[0], a_p2[0]) - TOLERANCE: return False
        if x > max(a_p1[0], a_p2[0]) + TOLERANCE: return False
        if y < min(a_p1[1], a_p2[1]) - TOLERANCE: return False
        if y > max(a_p1[1], a_p2[1]) + TOLERANCE: return False
        if x < min(b_p1[0], b_p2[0]) - TOLERANCE: return False
        if x > max(b_p1[0], b_p2[0]) + TOLERANCE: return False
        if y < min(b_p1[1], b_p2[1]) - TOLERANCE: return False
        if y > max(b_p1[1], b_p2[1]) + TOLERANCE: return False
    
        return x, y
        

if __name__ == "__main__":
    ars1_app = Ars1()
    ars1_app.on_execute()
