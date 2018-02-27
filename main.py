import pygame
from pygame.locals import *


class Ars1:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.posx = 300
        self.posy = 300
        self.velocity_base = 1
        self.vel_x = 0
        self.vel_y = 0
        self.size = self.weight, self.height = 800, 800
        self.time = pygame.time.get_ticks()

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
        delta_time = pygame.time.get_ticks() - self.time  # Calculate time since last frame
        self.time = pygame.time.get_ticks()  # Store current time at this frame
        self.posx = self.posx + int(self.vel_x * delta_time)  # Scale movement to time
        self.posy = self.posy + int(self.vel_y * delta_time)
        pass

    def on_render(self):
        self.redraw()
        pass

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
        self._display_surf.fill((255, 255, 255))
        self.circle = pygame.draw.circle(self._display_surf, (0, 0, 255), (self.posx, self.posy), 25, 0)
        pygame.display.update()


if __name__ == "__main__":
    ars1_app = Ars1()
    ars1_app.on_execute()
