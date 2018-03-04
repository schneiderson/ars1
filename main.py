import pygame
import math
from bot import robot as bot

pygame.font.init()
game_font = pygame.font.SysFont('arial', 16)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (66, 134, 244)
RED = (226, 123, 120)

GRAPHICS_ENABLED = True
TIME_DILATION = 4 # Time dilation can be used to speed up or slow down simulation. All time interactions are multiplied by this factor. 1 = realtime


class Ars1:
    def __init__(self):
        self._running = True
        self._display_surf = None
        
        self.robot = bot.Robot()
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
        
        # Display parameters
        self.size = self.width, self.height = 1000, 800
        self.frames = 0
        self.time = self.get_elapsed_time()
        
    def on_init(self):
        pygame.init()
        if GRAPHICS_ENABLED: self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        self.robot.update_sensors(self.walls)
        self.on_render()

    def on_event(self, event):
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
        # Calculate time since last frame
        current_time = self.get_elapsed_time()
        delta_time = current_time - self.time
        if delta_time - 20 > 0:
            self.time = current_time
            
            # Update robot position
            self.robot.move_robot(delta_time)
            
            # Update robot sensors
            self.robot.update_sensors(self.walls)

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

    def on_render(self):
        self.frames += 1

        debug = ["Debug info:",
                 "Realtime: " + str(pygame.time.get_ticks()) + " ms",
                 "Simulation time: " + str(self.get_elapsed_time()) + " ms",
                 "Time dilation: * " + str(TIME_DILATION),
                 "Frames: " + str(self.frames),
                 "FPS: " + str(self.frames / (pygame.time.get_ticks() / 1000)),
                 "",
                 "Robot:",
                 "Angle: " + str(self.robot.angle),
                 "Pos_x: " + str(self.robot.posx),
                 "Pos_y: " + str(self.robot.posy),
                 "Vel_left: " + str(self.robot.vel_left),
                 "Vel_right: " + str(self.robot.vel_right)]
        if not GRAPHICS_ENABLED:
            if self.get_elapsed_time() % (1000*TIME_DILATION) == 0:
                print("\n"*10)
                for index, info in enumerate(debug):
                    print(info)
        else:
            # Clean display
            self._display_surf.fill(WHITE)
    
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
                self._display_surf.blit(game_font.render(info, False, BLACK), (800,50+(index*15)))
            
            # Update display
            pygame.display.update()
            
    def get_elapsed_time(self):
        return int(pygame.time.get_ticks() * TIME_DILATION)

if __name__ == "__main__":
    ars1_app = Ars1()
    ars1_app.on_execute()
