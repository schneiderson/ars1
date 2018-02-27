import pygame
from pygame.locals import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

class Ars1:
    def __init__(self):
        self._running = True
        self._display_surf = None

        # Robot parameters
        self.posx = 300
        self.posy = 300

        # Walls
        self.walls = [
            # (x1,y1), (x2,y2)
            [(50, 50), (750, 50)],
            [(50, 750), (750, 750)],
            [(50, 50), (50, 750)],
            [(750, 50), (750, 750)],
        ]

        # Display parameters
        self.size = self.weight, self.height = 800, 800

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
                self.posx = self.posx - 10
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.posx = self.posx + 10
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.posy = self.posy - 10
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.posy = self.posy + 10

        self.redraw()

    def on_loop(self):
        pass

    def on_render(self):
        pass

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while (self._running):
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

        # Draw the robot
        pygame.draw.circle(self._display_surf, BLUE, (self.posx, self.posy), 25, 0)

        # Update display
        pygame.display.update()

if __name__ == "__main__":
    ars1_app = Ars1()
    ars1_app.on_execute()
