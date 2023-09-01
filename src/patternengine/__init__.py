"""A package to emit bullet patterns in bullet hell style shmups."""

from itertools import cycle
from random import random

from pgcooldown import Cooldown
from pygame import Vector2

# See Freya Holmer "The simple yet powerful math we don't talk about":
#     https://www.youtube.com/watch?v=R6UB7mVO3fY
#
# This is the "official" lerp, but it's about 10% slower than the one with only
# a single multiplication below.
# lerp     = lambda a, b, t: (1 - t) * a + b * t

lerp     = lambda a, b, t: t * (b - a) + a
inv_lerp = lambda a, b, v: (v - a) / (b - a)
remap    = lambda a0, a1, b0, b1, v: lerp(b0, b1, inv_lerp(a0, a1, v))


class Ring:
    """A ring shaped generator for bullet positions and momentum.

    Returns a generator object that provides the `BulletSource` class with an
    endless supply of projectiles.

    This class is probably not used itself directly.  It is just configuration
    for the `BulletSource` below.

    Right now, this is the only shape, and most examples of shmups I've seen
    don't use anything else.  Lines e.g. are rather uncommon, in contrast to
    normal particle systems.

    Bullets are emitted from along the rim of the ring the size being
    `radius`.

    To aim bullets or constraint the area the ring fires at can be controlled
    by the `aim` and `width`. The `aim` is the angle of the middle of the
    emitting arc, while the `width` is its angular size.

    `steps` controls into how much emitting points the arc or circle is split
    into.  The bullets will be emitted clockwise and in infinite number.

    `heartbeat` makes it possible to create bullet patterns within the ring or
    arc, e.g. 3 bullets besides each other, followed by a gap.

    Note that by making the length of `heartbeat` differ from `steps`, the
    ring can create irregular patterns.

    `randomize` overrides step and just gives random positions on the arc.

    The ring returns a tuple of a vector from its center to the position where
    the bullet is emitted from, and the same vector normalized to be used to
    control the speed and direction of the bullet.

    Note:
    -----
    The ring doesn't have a position, it only gives the emitted
    positions relative to its center.

    Note:
    -----
    When configured as an arc, start and end degrees specified by `width` are
    included while emitting.  

    In the case of a full circle, that is not the case, since 0 and 360
    degrees would result in twice as much emits as all other steps.

    This is calculated by this method, which returns normalized steps in an
    interval from 0 - 1.

        l = 1 / steps if width % 360 == 0 else 1 / (steps - 1)

    Parameters
    ----------
    radius: float
        Radius of the ring

    steps: int
        Number of steps the ring (or arc) is devided into.

    aim: float = 0
        If creating an arc, this is controls the direction the arc points
        towards in degrees with 0 degrees being right.

    width: float = 360
        Limit the angle of the arc.  Default is the full circle.  The arc is
        spread over `width / 2` to the left and right of `aim`

    randomize: bool = False
        Ignore `steps`, just emit from random points on the ring/arc.

    jitter: float = 0
        Amount of jitter in degrees that a bullet can vary from its actual path

    Attributes
    ----------
    `radius`, `aim`, `width`, `randomize` parameters above are also available
    as attributes and can be modified in runtime.

    `steps` can not be used as an attribute, since it is only used once to
    initialize the generator.

    Returns
    -------
    Generator[tuple[pygame.Vector2, pygame.Vector2]]

        1st vector of length `radius`, pointing from the origin to the launch
        spot on the ring/arc

        2nd vector same as 1st, but normalized to length of 1.

    """
    def __init__(self, radius, steps, aim=0, width=360,
                 randomize=False, heartbeat='#', jitter=0):
        self.radius = radius
        self._steps = steps
        self.aim = aim
        self._width = width
        self.randomize = randomize
        self.heartbeat = heartbeat
        self.jitter = jitter

        self.ts = self._new_t_iter()

    def _new_t_iter(self):
        step = 1 / self._steps if self._width == 360 else 1 / (self._steps - 1)
        return cycle([i * step for i in range(self._steps)])

    # Fcking not needed, but can't have setter without getter
    @property
    def steps(self): return self._steps  # noqa: E704

    @steps.setter
    def steps(self, steps):
        self._steps = steps
        self.ts = self._new_t_iter()

    @property
    def width(self): return self._width  # noqa: E704

    @width.setter
    def width(self, w):
        if w < 0:
            raise ValueError('Negative width not allowed')

        self._width = w
        if w != self._width and w == 360 or self._width == 360:
            self.ts = self._new_t_iter()

    @property
    def heartbeat(self): return self._heartbeat  # noqa: E704

    @heartbeat.setter
    def heartbeat(self, h):
        if '#' not in h: raise ValueError('Heartbeat contains no beats (#)')
        self._heartbeat = cycle(h)

    def _angle(self, t):
        """Return the angle within the aimed arc at step t"""
        # Can't precalc this, since aim or width might be changed

        phi = lerp(0, self._width, t) + self.aim
        if self.jitter:
            phi += random() * self.jitter - self.jitter / 2
        if self._width != 360:
            phi -= self._width / 2

        return phi

    def __iter__(self):
        return self

    def __next__(self):
        if self.randomize:
            t = random()
        else:
            t = next(self.ts)
            if next(self.heartbeat) != '#':
                return None

        v = Vector2(1, 0)
        v.rotate_ip(self._angle(t))

        return v * self.radius, v


class Heartbeat:
    """A generator for bullet emit events.

    The heartbeat is a string of arbitrary length where each pound sign stands
    for an emit.  The whole string is mapped onto a given time interval.

    Beat patterns can be easily created with this method.

    Given 2s interval and the pattern '#.......#.......' as input, the
    heartbeat, the program can pull the `next` value out of the heartbeat.
    Only if the proper time (duration / len(string)) has passed, *and* the
    next char is a pound sign, the result is `True`, otherwise it's false.

    Since *all* other characters are ignored, one can use above notation to
    visualize the beats, or embed the pound signs in counting digits like so:

        '#123#567#901#345'

    This way, it's easy to synchronize multiple bullet emitters by constructing their interval and heartbeats the same:

        a. '#.......#.......'
        b. '# #.....#.#.....'
        c. '.....#.......#..'

    Parameters
    ----------
    duration: pgcooldown.Cooldown | float
        A cooldown can be put in here directly, but if all patterns are
        predefined, it's useful to pass a float instead, since a cooldown
        would start to run as soon as it's instantiated.

    pattern: str
        The actual pattern.

    Returns
    -------
    Generator[bool]
        `True` = Emit command.

    """
    def __init__(self, duration, pattern):
        self.cooldown = Cooldown(duration / len(pattern), cold=True)
        self.c = cycle(pattern)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cooldown.hot:
            return False

        self.cooldown.reset(wrap=True)
        return next(self.c) == '#'


class BulletSource:
    """A generator for bullet patterns.

    This class is the glue between the ring that controls the position and
    momentum of a bullet, and the heartbeat, that controls when to release
    bullets.

    Note
    ----
    Do not include the  parameter in the Parameters section.

    Parameters
    ----------
    bullets: int
        Number of bullets to emit on a heartbeat.

    ring: patternengine.Ring
        An instance of the `Ring` class above, that configures position and
        momentum of bullets.

    heartbeat: patternengine.Heartbeat
        An instance of the `Heartbeat` class above, to trigger emits at
        defined intervals.

    aim: float = 0
        Alternative to control the `aim` of the `Ring` class.  Can be used to
        point an arc towards a specific direction, e.g. a vector to a target.


    Attributes
    ----------
    None

    Returns
    -------
    Generator[list[tuple[pygame.Vector2, pygame.Vector2]]]

        A list of bullets.  A bullet is a tuple of two vectors, one pointing
        from its center to the emit point on the arc, the other giving the
        direction to be used as a multiplier with a bullet speed.

        [ (v_a, v_a_normalized),
          (v_b, b_b_normalized),
          ... ]

    """
    def __init__(self, bullets, ring, heartbeat, aim=0):
        self.bullets = bullets
        self.ring = ring
        self.heartbeat = heartbeat
        self.aim = aim

    def __iter__(self):
        return self

    def __next__(self):
        res = []
        while next(self.heartbeat):
            for i in range(self.bullets):
                if not (bullet := next(self.ring)):
                    continue

                offset, momentum = bullet
                if self.aim:
                    res.append((offset.rotate(self.aim), momentum.rotate(self.aim)))
                else:
                    res.append((offset, momentum))
        return res
