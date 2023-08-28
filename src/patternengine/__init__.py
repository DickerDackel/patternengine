from itertools import cycle
from random import uniform

from pgcooldown import Cooldown
from pygame import Vector2


class Ring:
    def __init__(self, radius, steps, phi0=0, phi1=360, randomize=False):
        self.radius = radius
        self.steps = steps
        self.phi0 = phi0
        self.phi1 = phi1
        self.randomize = False

        if abs(phi1 - phi0) == 360:
            l = 1 / steps
        else:
            l = 1 / (steps - 1)
        self.ts = cycle([i * l for i in range(steps)])

        self.angle = 0

    def __iter__(self):
        return self

    def __next__(self):
        lerp = lambda a, b, t: t * (b - a) + a

        if self.randomize:
            self.angle = uniform(self.phi0, self.phi1)
        else:
            t = next(self.ts)
            self.angle = lerp(self.phi0, self.phi1, t)

        v = Vector2(1, 0)
        v.rotate_ip(self.angle)

        return v * self.radius, v


class Heartbeat:
    def __init__(self, duration, pattern):
        self.cooldown = Cooldown(duration / len(pattern))
        self.c = cycle(pattern)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cooldown.hot:
            return

        self.cooldown.reset()
        return next(self.c) == '#'


class BulletSource:
    def __init__(self, bullets, ring, heartbeat, aim=0):
        self.bullets = bullets
        self.ring = ring
        self.heartbeat = heartbeat
        self.aim = aim

    def __iter__(self):
        return self

    def __next__(self):
        if not next(self.heartbeat):
            return []

        res = []
        for i in range(self.bullets):
            offset, momentum = next(self.ring)
            if self.aim:
                res.append((offset.rotate(self.aim), momentum.rotate(self.aim)))
            else:
                res.append((offset, momentum))
        return res


def bullet_source_rotate_system(dt, eid, bullet_source, angular_momentum):
    bullet_source.aim = angular_momentum()


def bullet_source_system(dt, eid, bullet_source, bullet_factory, position):
    for offset, momentum in next(bullet_source):
        bullet_factory(position + offset, momentum)
