import pygame
import math
from pygame.locals import *

pygame.font.init()
game_font = pygame.font.SysFont('Comic Sans MS', 12)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

class Ars1:
    def __init__(self):
        self._running = True
        self._display_surf = None

        # Robot parameters
        self.robot_radius = 30
        self.posx = 100
        self.posy = 100
        self.previous_posx = self.posx
        self.previous_posy = self.posy
        self.velocity_base = 1
        self.vel_x = 0
        self.vel_y = 0

        # Walls
        self.walls = [
            # (x1,y1), (x2,y2)
            
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
        self.sensors = [(0, (0,0))] * 12

        # Display parameters
        self.size = self.width, self.height = 800, 800
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

        self.redraw()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.vel_x = self.vel_x - self.velocity_base
            if event.key == pygame.K_RIGHT:
                self.vel_x = self.vel_x + self.velocity_base
            if event.key == pygame.K_UP:
                self.vel_y = self.vel_y - self.velocity_base
            if event.key == pygame.K_DOWN:
                self.vel_y = self.vel_y + self.velocity_base
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.vel_x = self.vel_x + self.velocity_base
            if event.key == pygame.K_RIGHT:
                self.vel_x = self.vel_x - self.velocity_base
            if event.key == pygame.K_UP:
                self.vel_y = self.vel_y + self.velocity_base
            if event.key == pygame.K_DOWN:
                self.vel_y = self.vel_y - self.velocity_base

        self.redraw()

    def on_loop(self):
        # Update position
        delta_time = pygame.time.get_ticks() - self.time  # Calculate time since last frame
        self.time = pygame.time.get_ticks()  # Store current time at this frame
        posx = self.posx + int(self.vel_x * delta_time)  # Scale movement to time
        posy = self.posy + int(self.vel_y * delta_time)
        self.update_robot_posx(posx)
        self.update_robot_posy(posy)
        
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
        # Clean display
        self._display_surf.fill((255, 255, 255))

        # Draw walls
        for w in self.walls:
            pygame.draw.line(self._display_surf, BLACK, w[0], w[1])
        
        # Draw sensors
        robot_pos = (self.posx, self.posy)
        for index, sensor in enumerate(self.sensors):
            pygame.draw.line(self._display_surf, RED, robot_pos, sensor[1])
            textsurface = game_font.render("{0:.0f}".format(sensor[0]), False, RED)
            self._display_surf.blit(textsurface, sensor[1])
            
        # Draw the robot
        pygame.draw.circle(self._display_surf, BLUE, robot_pos, self.robot_radius, 0)
            
        # Update display
        pygame.display.update()

    # Update all sensor values and positions
    def update_sensors(self):
        if (self.previous_posx == self.posx and self.previous_posy == self.posy): return True
        for index, sensor in enumerate(self.sensors):
            # Determine current sensor endpoint
            closest_collision = 300
            angle = (360 / len(self.sensors)) * index
            theta_rad = math.pi / 2 - math.radians(angle)
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
                        
            # Update sensor value
            self.sensors[index] = [closest_collision, sensor_end]
            
            # TODO: if any sensor reaches a closest_collision < radius of our robot, throw a collision event
            if closest_collision < self.robot_radius:
                # print('collided with wall!')
                # Restore previous position
                self.update_robot_posx(self.previous_posx)
                self.update_robot_posy(self.previous_posy)

    # Finds the intersection between two lines a and b defined by their respective endpoints p1 and p2
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
