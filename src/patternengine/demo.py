import pygame
import tinyecs as ecs
import tinyecs.compsys as ecsc

import patternengine as pe

from functools import lru_cache, partial

from pgcooldown import Cooldown, CronD, LerpThing
from pygame import Vector2
from pygamehelpers.framework import GameState
from rpeasings import *  # noqa: F401, F403

from patternengine.config import States

sprite_group = pygame.sprite.Group()


@lru_cache
def bullet_image_factory(r0, r1, w, c0, c1, c2=None):
    size = 2 * r1 if r1 else 2 * r0
    image = pygame.Surface((size, size))
    image.set_colorkey('black')
    rect = image.get_rect()

    c0 = pygame.Color(c0)
    c1 = pygame.Color(c1)

    for i in range(0, r0 - 1):
        t = out_sine(i / r0)  # noqa: F405
        color = c1.lerp(c0, t)
        r = r0 - i
        pygame.draw.circle(image, color, rect.center, r)

    if r1:
        if not c2:
            c2 = c0
        pygame.draw.circle(image, c2, rect.center, r1, width=w)

    return image


def bullet_factory(position, momentum, speed, image, sprite_group, **kwargs):
    e = ecs.create_entity()
    ecs.add_component(e, 'position', position)
    ecs.add_component(e, 'momentum', momentum * speed)
    ecs.add_component(e, 'sprite', ecsc.ESprite(sprite_group, image=image))
    ecs.add_component(e, 'world', True)

    for cid, comp in kwargs.items():
        if cid == 'lifetime':
            comp = Cooldown(comp)
        ecs.add_component(e, cid, comp)

    return e


bullet_images = {
    'hotpink': bullet_image_factory(8, 0, 1, 'white', 'hotpink', 'hotpink'),
    'cyan': bullet_image_factory(8, 0, 1, 'cyan', 'darkblue', 'cyan'),
    'yellow': bullet_image_factory(9, 12, 1, 'yellow', 'darkorange', 'darkorange'),
    'lightblue': bullet_image_factory(13, 16, 1, 'white', 'lightblue', 'lightblue'),
    'green': bullet_image_factory(6, 8, 1, 'yellow', 'green', 'green'),
    'red': bullet_image_factory(4, 0, 1, 'red', 'brown', 'red'),
}

bullet_factories = {
    'hotpink': partial(bullet_factory, sprite_group=sprite_group, image=bullet_images['hotpink']),
    'cyan': partial(bullet_factory, sprite_group=sprite_group, image=bullet_images['cyan']),
    'yellow': partial(bullet_factory, sprite_group=sprite_group, image=bullet_images['yellow']),
    'lightblue': partial(bullet_factory, sprite_group=sprite_group, image=bullet_images['lightblue']),
    'green': partial(bullet_factory, sprite_group=sprite_group, image=bullet_images['green']),
    'red': partial(bullet_factory, sprite_group=sprite_group, image=bullet_images['red']),
}


def pattern_factory(position, bullet_source, bullet_factory, **kwargs):
    if not isinstance(position, Vector2):
        position = Vector2(position)
    e = ecs.create_entity()
    ecs.add_component(e, 'position', position)
    ecs.add_component(e, 'bullet_source', bullet_source)
    ecs.add_component(e, 'bullet_factory', bullet_factory)
    for cid, comp in kwargs.items():
        ecs.add_component(e, cid, comp)
    return e


class Demo(GameState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.group = pygame.sprite.Group()

        self.font = pygame.Font(None, 48)
        self.label = pygame.sprite.Sprite(self.group)
        self.label.image = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.label.rect = pygame.Rect(0, 0, 2, 2)
        self.label.rect.center = (self.app.rect.centerx, 50)

        self.countdown_sprites = []
        font = pygame.Font(None, 64)
        for s in ['3', '2', '1', 'Go!']:
            sprite = pygame.sprite.Sprite()
            sprite.image = font.render(s, True, 'white')
            sprite.rect = sprite.image.get_rect(center=self.app.rect.center)
            self.countdown_sprites.append(sprite)

        self.countdown_group = pygame.sprite.Group()
        self.countdown_cooldown = Cooldown(1, cold=True)
        self.countdown = None

        self.crond = CronD()
        self.deadzone = self.app.rect.scale_by(1.25)

        self.reset()

    def update_label(self, s):
        self.label.image = self.font.render(s, True, 'white')
        self.label.rect = self.label.image.get_rect(center=self.label.rect.center)

    def reset(self, *args, **kwargs):
        super().reset(*args, **kwargs)
        # No need to reset the countdown cooldown, since we should start cold
        # anyways
        self.countdown = iter(self.countdown_sprites)

        self.crond.heap.clear()

        rect = self.app.rect
        t = 3
        # self.crond.add(t, partial(self.update_label, 'Simple 4 step ring'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=4,
        #                               ring=pe.Ring(50, 4),
        #                               heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
        #                           bullet_factory=partial(bullet_factories['hotpink'], speed=100),
        #                           lifetime=10))
        # t += 10
        # self.crond.add(t, partial(self.update_label, 'Ring stack'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=18,
        #                               ring=pe.Ring(50, 18),
        #                               heartbeat=pe.Heartbeat(2, '#.#.#.#.#...............................')),
        #                           bullet_factory=partial(bullet_factories['cyan'], speed=100),
        #                           lifetime=10))

        # t += 10
        # self.crond.add(t, partial(self.update_label, 'Simple ring + Stack with 10° aim'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=18,
        #                               ring=pe.Ring(50, 18),
        #                               heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
        #                           bullet_factory=partial(bullet_factories['hotpink'], speed=100),
        #                           lifetime=10))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=18,
        #                               ring=pe.Ring(50, 18),
        #                               heartbeat=pe.Heartbeat(2, '#.#.#.#.#...............................'),
        #                               aim=10),
        #                           bullet_factory=partial(bullet_factories['cyan'], speed=100),
        #                           lifetime=10))
        # t += 10
        # self.crond.add(t, partial(self.update_label, 'Ring with 5 steps'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=5,
        #                               ring=pe.Ring(50, 5),
        #                               heartbeat=pe.Heartbeat(2, '#.......................................')),
        #                           bullet_factory=partial(bullet_factories['yellow'], speed=100),
        #                           lifetime=10))
        # t += 10
        # self.crond.add(t, partial(self.update_label, 'Ring with 2 steps, rotating'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=2,
        #                               ring=pe.Ring(10, 2),
        #                               heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           rotation=LerpThing(0, 360, 8, repeat=1),
        #                           lifetime=3))

        # t += 3
        # self.crond.add(t, partial(self.update_label, 'Ring with 4 steps, rotating'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=4,
        #                               ring=pe.Ring(10, 4),
        #                               heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           rotation=LerpThing(0, 360, 8, repeat=1),
        #                           lifetime=3))
        # t += 3
        # self.crond.add(t, partial(self.update_label, 'Ring with 8 steps, rotating'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=8,
        #                               ring=pe.Ring(10, 8),
        #                               heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           rotation=LerpThing(0, 360, 8, repeat=1),
        #                           lifetime=3))
        # t += 3
        # self.crond.add(t, partial(self.update_label, 'Ring with 18 steps, rotating'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=18,
        #                               ring=pe.Ring(10, 18),
        #                               heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           rotation=LerpThing(0, 360, 8, repeat=1),
        #                           lifetime=3))
        # t += 3
        # self.crond.add(t, partial(self.update_label, 'Ring with 36 steps, rotating'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=36,
        #                               ring=pe.Ring(10, 36),
        #                               heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           rotation=LerpThing(0, 360, 8, repeat=1),
        #                           lifetime=3))
        # t += 6
        # self.crond.add(t, partial(self.update_label, 'Ring with 1 step, rotating'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=rect.center,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=1,
        #                               ring=pe.Ring(50, 1),
        #                               heartbeat=pe.Heartbeat(2, '########################################')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           rotation=LerpThing(0, 360, 2, repeat=1),
        #                           lifetime=10))
        # t += 10
        # self.crond.add(t, partial(self.update_label, 'Half rings'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=(rect.centerx, 50),
        #                           bullet_source=pe.BulletSource(
        #                               bullets=18,
        #                               ring=pe.Ring(50, 18, phi0=0, phi1=180),
        #                               heartbeat=pe.Heartbeat(2, '#...#...#...#...#...#...#...#...#...#...')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           lifetime=10))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=(rect.centerx, rect.height - 50),
        #                           bullet_source=pe.BulletSource(
        #                               bullets=18,
        #                               ring=pe.Ring(50, 18, phi0=0, phi1=-180),
        #                               heartbeat=pe.Heartbeat(2, '#...#...#...#...#...#...#...#...#...#...')),
        #                           bullet_factory=partial(bullet_factories['green'], speed=100),
        #                           lifetime=10))
        # t += 5
        # self.crond.add(t, partial(self.update_label, 'Half + quarter rings'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=(50, 50),
        #                           bullet_source=pe.BulletSource(
        #                               bullets=9,
        #                               ring=pe.Ring(50, 9, phi0=0, phi1=90),
        #                               heartbeat=pe.Heartbeat(2, '#...#...#...#...#...#...#...#...#...#...')),
        #                           bullet_factory=partial(bullet_factories['cyan'], speed=100),
        #                           lifetime=5))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=(rect.width - 50, rect.height - 50),
        #                           bullet_source=pe.BulletSource(
        #                               bullets=9,
        #                               ring=pe.Ring(50, 9, phi0=-90, phi1=-180),
        #                               heartbeat=pe.Heartbeat(2, '#...#...#...#...#...#...#...#...#...#...')),
        #                           bullet_factory=partial(bullet_factories['cyan'], speed=100),
        #                           lifetime=5))
        # t += 5
        # self.crond.add(t, partial(self.update_label, 'oscillating partial ring'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=(rect.centerx, 50),
        #                           bullet_source=pe.BulletSource(
        #                               bullets=5,
        #                               ring=pe.Ring(50, 5, phi0=-30, phi1=30),
        #                               heartbeat=pe.Heartbeat(2, '#...#...#...#...#...#...#...#...#...#...')),
        #                           bullet_factory=partial(bullet_factories['hotpink'], speed=200),
        #                           rotation=LerpThing(165, 15, 5, repeat=2),
        #                           lifetime=15))
        # t += 15
        # self.crond.add(t, partial(self.update_label, 'Rotating 5 step ring in motion'))
        # self.crond.add(t, partial(pattern_factory,
        #                           position=(50, 50),
        #                           momentum=Vector2(1024, 768).normalize() * 100,
        #                           bullet_source=pe.BulletSource(
        #                               bullets=5,
        #                               ring=pe.Ring(50, 5),
        #                               heartbeat=pe.Heartbeat(2, '#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.')),
        #                           bullet_factory=partial(bullet_factories['yellow'], speed=10, lifetime=10),
        #                           rotation=LerpThing(0, 360, 8, repeat=1),
        #                           lifetime=15))
        # t += 15
        self.crond.add(t, partial(self.update_label, 'Don\'t use python, it\'s too slow...'))
        t += 3
        self.crond.add(t, partial(pattern_factory,
                                  position=(100, 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=8,
                                      ring=pe.Ring(25, 8),
                                      heartbeat=pe.Heartbeat(2, '###.....................................')),
                                  bullet_factory=partial(bullet_factories['cyan'], speed=100),
                                  lifetime=45))
        self.crond.add(t, partial(pattern_factory,
                                  position=(rect.width - 100, 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=8,
                                      ring=pe.Ring(25, 8),
                                      heartbeat=pe.Heartbeat(2, '###.....................................')),
                                  bullet_factory=partial(bullet_factories['cyan'], speed=100),
                                  lifetime=45))

        t += 10
        self.crond.add(t, partial(pattern_factory,
                                  position=(100, 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=36,
                                      ring=pe.Ring(50, 36),
                                      heartbeat=pe.Heartbeat(2, '..........#...................#.........')),
                                  bullet_factory=partial(bullet_factories['hotpink'], speed=100),
                                  lifetime=10))
        self.crond.add(t, partial(pattern_factory,
                                  position=(rect.width - 100, 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=36,
                                      ring=pe.Ring(50, 36),
                                      heartbeat=pe.Heartbeat(2, '..........#...................#.........')),
                                  bullet_factory=partial(bullet_factories['hotpink'], speed=100),
                                  lifetime=10))

        t += 10
        self.crond.add(t, partial(pattern_factory,
                                  position=(100, 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=36,
                                      ring=pe.Ring(50, 36),
                                      heartbeat=pe.Heartbeat(2, '#...#...#...#...#...#...#...#...#...#...')),
                                  bullet_factory=partial(bullet_factories['hotpink'], speed=100),
                                  lifetime=25))
        self.crond.add(t, partial(pattern_factory,
                                  position=(rect.width - 100, 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=36,
                                      ring=pe.Ring(50, 36),
                                      heartbeat=pe.Heartbeat(2, '#...#...#...#...#...#...#...#...#...#...')),
                                  bullet_factory=partial(bullet_factories['hotpink'], speed=100),
                                  lifetime=25))

        t += 5
        self.crond.add(t, partial(pattern_factory,
                                  position=(100, rect.height - 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=10,
                                      ring=pe.Ring(30, 10),
                                      heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
                                  bullet_factory=partial(bullet_factories['green'], speed=100, angular_momentum=45, lifetime=10),
                                  lifetime=20))
        self.crond.add(t, partial(pattern_factory,
                                  position=(rect.width - 100, rect.height - 100),
                                  bullet_source=pe.BulletSource(
                                      bullets=10,
                                      ring=pe.Ring(30, 10),
                                      heartbeat=pe.Heartbeat(2, '#....#....#....#....#....#....#....#....')),
                                  bullet_factory=partial(bullet_factories['green'], speed=100, angular_momentum=45, lifetime=10),
                                  lifetime=20))

        t += 5
        self.crond.add(t, partial(pattern_factory,
                                  position=rect.center,
                                  bullet_source=pe.BulletSource(
                                      bullets=16,
                                      ring=pe.Ring(100, 16),
                                      heartbeat=pe.Heartbeat(2, '#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.')),
                                  bullet_factory=partial(bullet_factories['yellow'], speed=100),
                                  rotation=LerpThing(0, 360, 5, repeat=1),
                                  lifetime=15))

        t += 5
        self.crond.add(t, partial(pattern_factory,
                                  position=rect.center,
                                  bullet_source=pe.BulletSource(
                                      bullets=8,
                                      ring=pe.Ring(100, 8),
                                      heartbeat=pe.Heartbeat(4, '#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.')),
                                  bullet_factory=partial(bullet_factories['lightblue'], speed=-100, angular_momentum=10),
                                  rotation=LerpThing(0, 360, 5, repeat=1),
                                  lifetime=10))

        t += 5
        self.crond.add(t, partial(pattern_factory,
                                  position=rect.center,
                                  bullet_source=pe.BulletSource(
                                      bullets=2,
                                      ring=pe.Ring(0, 2),
                                      heartbeat=pe.Heartbeat(1, '#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.#.')),
                                  bullet_factory=partial(bullet_factories['red'], speed=150, angular_momentum=35, lifetime=20),
                                  rotation=LerpThing(0, 360, 1, repeat=1),
                                  lifetime=15))
        t += 35

        self.crond.add(t, partial(self.update_label, ''))
        t += 3

        def done():
            raise SystemExit

        self.crond.add(t, done)

    def do_countdown(self):
        if self.countdown:
            if self.countdown_cooldown.cold:
                self.countdown_cooldown.reset()
                self.countdown_group.empty()
                try:
                    self.countdown_group.add(next(self.countdown))
                except StopIteration:
                    self.countdown = None

    def update(self, dt):
        self.do_countdown()

        sprite_group.update(dt)
        self.group.update(dt)

        def angular_momentum_system(dt, eid, angular_momentum, momentum):
            momentum.rotate_ip(angular_momentum * dt)

        def circle_system(dt, eid, circle, position, *, surface):
            pygame.draw.circle(surface, circle[1], position, circle[0], width=1)

        self.crond.update()

        ecs.run_system(dt, pe.bullet_source_rotate_system, 'bullet_source', 'rotation')
        ecs.run_system(dt, pe.bullet_source_system, 'bullet_source', 'bullet_factory', 'position')
        ecs.run_system(dt, angular_momentum_system, 'angular_momentum', 'momentum')
        ecs.run_system(dt, ecsc.momentum_system, 'momentum', 'position')
        ecs.run_system(dt, ecsc.sprite_system, 'sprite', 'position')
        ecs.run_system(dt, ecsc.deadzone_system, 'world', 'position', container=self.deadzone)
        ecs.run_system(dt, ecsc.lifetime_system, 'lifetime')

    def draw(self, screen):
        screen.fill('black')

        sprite_group.draw(screen)
        self.group.draw(screen)
        self.countdown_group.draw(screen)
        # def pin_system(dt, eid, bullet_source, position):
        #     v = Vector2()
        #     v.from_polar((100, bullet_source.aim))
        #     pygame.draw.line(screen, 'grey30', position, position + v)
        #     pygame.draw.circle(screen, 'yellow', position, 50, width=1)
        # ecs.run_system(1, pin_system, 'bullet_source', 'position')

        sprites = len(sprite_group)
        pygame.display.set_caption(f'{self.app.title} - time={pygame.time.get_ticks()/1000:.2f}  fps={self.app.clock.get_fps():.2f}  {sprites=}')
