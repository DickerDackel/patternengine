#!/bin/env python3

from os import environ
from random import triangular

import glm
import pygame

from glm import vec2
from pgcooldown import Cooldown
from rpeasings import easings

from patternengine import BulletSource, Heartbeat, Line, Disk, Point, Rectangle, Ring

if environ.get('XDG_SESSION_TYPE', '') == 'wayland':
    environ['SDL_VIDEODRIVER'] = 'wayland'

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1920, 1080)
FPS = 60
DT_MAX = 3 / FPS


class ZeSprite(pygame.sprite.Sprite):
    image = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(image, 'yellow', (7, 7), 7)
    world = SCREEN.inflate((16, 16))

    def __init__(self, pos, momentum, *groups):
        super().__init__(*groups)
        self.image = ZeSprite.image.copy()
        self.pos = vec2(pos)
        self.momentum = momentum
        self.rect = ZeSprite.image.get_rect(center=glm.round(self.pos))
        self.cooldown = Cooldown(2)

    def update(self, dt):
        if self.cooldown.cold():
            self.kill()

        self.image.set_alpha(255 - easings['out_quad'](self.cooldown.normalized) * 255)
        self.pos += self.momentum * dt
        self.rect.center = glm.round(self.pos)

        if not ZeSprite.world.collidepoint(self.pos):
            self.kill()


def main():
    pygame.init()
    clock = pygame.time.Clock()
    window = pygame.Window(size=SCREEN.size, title=TITLE)
    screen = window.get_surface()

    font = pygame.font.SysFont(None, 24)

    group = pygame.sprite.Group()

    cell = SCREEN.scale_by(1 / 3).move_to(topleft=(0, 0))
    step_x = SCREEN.width / 3
    step_y = SCREEN.height / 3
    demos = []

    rect = cell.move_to(topleft=(0, 0))
    heartbeat = Heartbeat(0.01, '#')
    ring = Disk(20, rng=glm.diskRand)
    emitter = BulletSource(3, ring, heartbeat)
    label = font.render('Disk(20, rng=glm.diskRand)', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(step_x, 0))
    heartbeat = Heartbeat(0.15, '#')
    ring = Line(45, 100, 8)
    emitter = BulletSource(1, ring, heartbeat)
    label = font.render('Line(45, 100, 8)', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(2 * step_x, 0))
    heartbeat = Heartbeat(0.01, '#')
    ring = Line(45, 100, randomize=True, rng=lambda: glm.gaussRand(0.5, 0.5))
    emitter = BulletSource(3, ring, heartbeat)
    label = font.render('Line(45, 100, randomize=True, rng=gaussian)', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(0, step_y))
    heartbeat = Heartbeat(0.01, '#')
    ring = Point()
    emitter = BulletSource(3, ring, heartbeat)
    label = font.render('Point()', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(step_x, step_y))
    heartbeat = Heartbeat(0.5, '#')
    ring = Point(0)
    emitter = BulletSource(1, ring, heartbeat)
    label = font.render('Point(0)', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(2 * step_x, step_y))
    heartbeat = Heartbeat(0.01, '#')
    ring = Rectangle(100, 33)
    emitter = BulletSource(3, ring, heartbeat)
    label = font.render('Rectangle(100, 33)', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(0, 2 * step_y))
    heartbeat = Heartbeat(0.05, '#')
    ring = Ring(50, 12)
    emitter = BulletSource(1, ring, heartbeat)
    label = font.render('Ring(50, 12)', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(step_x, 2 * step_y))
    heartbeat = Heartbeat(0.01, '#')
    ring = Ring(50, 12, randomize=True)
    emitter = BulletSource(3, ring, heartbeat)
    label = font.render('Ring(50, 12, randomize=True)', True, 'white')
    demos.append((rect, emitter, label))

    rect = cell.move_to(topleft=(2 * step_x, 2 * step_y))
    heartbeat = Heartbeat(0.01, '#')
    ring = Ring(50, 12, width=90, aim=-90, randomize=True)
    emitter = BulletSource(3, ring, heartbeat)
    label = font.render('Ring(50, 12, width=90, aim=-90, randomize=True)', True, 'white')
    demos.append((rect, emitter, label))

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, DT_MAX)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_q and e.mod & pygame.KMOD_CTRL:
                    running = False

        screen.fill('black')

        for rect, emitter, label in demos:
            for pos, momentum in next(emitter):
                group.add(ZeSprite(vec2(rect.center) + pos, momentum * 75))
            screen.blit(label, label.get_rect(midbottom=rect.midbottom))

        group.update(dt)
        group.draw(screen)

        for rect, _, _ in demos:
            pygame.draw.circle(screen, 'red', rect.center, 4, width=2)

        window.flip()
        window.title = f'{TITLE} - time={pygame.time.get_ticks() / 1000:.2f}  fps={clock.get_fps():.2f}'

if __name__ == "__main__":
    main()
