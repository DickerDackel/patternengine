import glm

from itertools import cycle
from random import random

from pgcooldown import Cooldown
from glm import vec2

from patternengine.poms import POMS, MutatorStack


__all__ = ['Ring', 'Heartbeat', 'BulletSource', 'Stack', 'Fan', 'Factory']

########################################################################
# See Freya Holmer "The simple yet powerful math we don't talk about":
#     https://www.youtube.com/watch?v=R6UB7mVO3fY
#
# This is the "official" lerp, but it's about 10% slower than the one with only
# a single multiplication below.
# lerp     = lambda a, b, t: (1 - t) * a + b * t
#
lerp     = lambda a, b, t: t * (b - a) + a
inv_lerp = lambda a, b, v: (v - a) / (b - a)
remap    = lambda a0, a1, b0, b1, v: lerp(b0, b1, inv_lerp(a0, a1, v))
#
########################################################################


def _arc_steps(phi, steps):
    """Chunk an arc into steps.

    If it's a full circle, don't include both 0 and 360 degrees.
    """
    return 1 / steps if phi == 360 or steps == 1 else 1 / (steps - 1)


def _arc_cycle(arc, steps):
    """Return a cycle over `steps` within `arc`."""
    step = arc * _arc_steps(arc, steps)

    recenter = 0 if arc == 360 else arc / 2
    return cycle([step * i - recenter for i in range(steps)])


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

    Note, that aim can also be a callable that is expected to generate angles.

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

    aim: float = 0 | Callable[[], float]
        If creating an arc, this is controls the direction the arc points
        towards in degrees with 0 degrees being right.

        If this is a callable, then it will be called and is expected to
        return an angle.  To provide automatic rotation, e.g. use a
        `LerpThing(0, 360, duration)`

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
    Generator[tuple[vec2, vec2]]

        1st vector of length `radius`, pointing from the origin to the launch
        spot on the ring/arc

        2nd vector same as 1st, but normalized to length of 1.

    """
    def __init__(self, radius, steps, aim=0, width=360,
                 randomize=False, heartbeat='#', jitter=0):
        self.radius = radius
        self.steps = steps
        self._aim = aim if callable(aim) else lambda: aim
        self.width = width
        self.randomize = randomize
        self.heartbeat = cycle(heartbeat)
        self.jitter = jitter

        self.arc = _arc_cycle(self.width, self.steps)

    @property
    def aim(self): return self._aim()  # noqa: E704

    @aim.setter
    def aim(self, aim):
        self._aim = aim if callable(aim) else lambda: aim

    def __iter__(self):
        return self

    def __next__(self):
        if self.randomize:
            phi = random() * self.width
        else:
            phi = next(self.arc)
            if next(self.heartbeat) != '#':
                return None

        v = vec2(1, 0)
        v = glm.rotate(v, glm.radians(phi + self._aim()))

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
        if self.cooldown.hot():
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

    aim: float = 0 | Callable[[], float]
        Alternative to control the `aim` of the `Ring` class.  Can be used to
        point an arc towards a specific direction, e.g. a vector to a target.

        If this is a callable, then it will be called and is expected to
        return an angle.  To provide automatic rotation, e.g. use a
        `LerpThing(0, 360, duration)`


    Attributes
    ----------
    None

    Returns
    -------
    Generator[list[tuple[vec2, vec2]]]

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
        if not next(self.heartbeat):
            return []

        res = []
        for i in range(self.bullets):
            # Count blanks, but don't add them to res
            if not (bullet := next(self.ring)):
                continue

            offset, momentum = bullet
            if self.aim:
                phi = glm.radians(self.aim)
                res.append((glm.rotate(offset, phi),
                            glm.rotate(momentum, phi)))
            else:
                res.append((offset, momentum))
        return res

    @property
    def aim(self): return self._aim()  # noqa: E704

    @aim.setter
    def aim(self, aim):
        self._aim = aim if callable(aim) else lambda: aim


class Stack:
    """Stack an emitted ring.

    Pass the `Stack` instance to the `Factory` instead of the `BulletSource`.

    Instead of increasing the emit frequency of a ring, to release a stack of
    bullets, this class can be used.

    It gets one emit from a bullet source and copies it a given number of
    times.  Since all emitted bullets in a stack would have been the same
    speed and thus be placed exactly on top of each other, a speed gain factor
    is introduced, that scales the momentum of each level in the stack up by a
    small amount.

    This results in a stack of bullets that emit from a single point, but then
    spread out in the direction of their momentum.  See `pe-demo 01` for an
    example.

    Parameters
    ----------
    bullet_source: BulletSource
        The preconfigured bullet source, consisting of a ring and a heartbeat.
        See above.
    height: int
        The height of the stack
    gain: float
        The factor to upscale the momentum for each level in the stack.  The
        higher the gain, the further the emitted bullets spread out along
        their flight path.

    """

    def __init__(self, bullet_source, height, gain):
        self.bullet_source = bullet_source
        self.height = height
        self.gain = gain

    def __iter__(self):
        return self

    def __next__(self):
        res = []
        for position, momentum in next(self.bullet_source):
            for i in range(self.height):
                gain = self.gain ** i
                res.append((vec2(position), momentum * gain))
        return res


class Fan:
    """Fan out an emitted ring.

    Instead of increasing the number of bullets per ring emit, bullets can be
    fanned out over an angle.  So this is the "horizontal" counterpart to the
    "vertical" stack.

    It gets one emit from a bullet source and copies it a given number of
    times.  The fan is centered around the initially emitted bullet.  The
    `arc` of the fan is split um into `steps` pieces.

    Note
    ----
    Pass the `Fan` instance to the `Factory` instead of the `BulletSource`.
    A `Stack` can also be fanned out.

    Parameters
    ----------
    bullet_source: BulletSource
        The preconfigured bullet source, consisting of a ring and a heartbeat.
        See above.
    arc: float
        The angle width of the fan, centered around the initial bullet position.
    steps: int
        The number of steps the fan is segmented into.
    """
    def __init__(self, bullet_source, arc, steps):
        self.bullet_source = bullet_source
        self.arc = arc
        self.steps = steps

        self.arc = _arc_cycle(arc, steps)

    def __iter__(self):
        return self

    def __next__(self):
        res = []
        for position, momentum in next(self.bullet_source):
            for degrees, _ in zip(self.arc, range(self.steps)):
                phi = glm.radians(degrees)
                res.append((glm.rotate(position, phi),
                            glm.rotate(momentum, phi)))
        return res


class Factory:
    """A bullet pattern factory.

    The `Factory` will take the emit signals from a `BulletSource` and call a
    sprite factory for every emitted bullet.

    The sprite factory will receive a position and a momentum vector from the
    factory.  By default, the position vector of the Ring will be centered at
    `(0, 0)`.  If the Factory has a POMS attribute (see below), its position
    will be added to the position vector from the `Ring`.

    The momentum vector will be normalized (set to length 0), and needs to be
    scaled up with the required bullet speed by the sprite factory.  If the
    `Factory` has a `POMS` attribute with `orientation`, the momentum vector
    for the bullet will be rotated by that amount.

    If the `Factory` has a `POMS` attribute with momentum, that is passed as
    `factory_momentum` kwarg to the sprite factory.

    To pre-configure a sprite factory, use a partial that feeds in all
    required settings, or write a custom class that supports `call`.

    Besides a `POMS`, the `Factory` will also accept a list of mutators that
    can modify the `POMS` e.g. move or rotate the Factory across the screen.

    Parameters
    ----------
    bullet_source: BulletSource
        A preconfigured bullet source.  See above.
    sprite_factory: Callable
        A callback that creates a sprite from a position and momentum vector.
    poms: POMS = None
        Optional (P)osition, (O)rientation, (M)omentum and (S)pin for the Factory.

    """
    def __init__(self, bullet_source, sprite_factory, poms=None, mutators=None):
        self.bullet_source = bullet_source
        self.sprite_factory = sprite_factory
        self.poms = poms if poms else POMS(vec2(), 0, vec2(), 0)
        self.mutators = MutatorStack()
        if mutators:
            for m in mutators:
                self.mutators.add(m)

    def update(self, dt):
        self.mutators.run(dt)

        angle = glm.radians(self.poms.orientation)

        for position, momentum in next(self.bullet_source):
            if angle:
                position = glm.rotate(position, angle)
                momentum = glm.rotate(momentum, angle)
            self.sprite_factory(position + self.poms.position,
                                momentum, factory_momentum=self.poms.momentum)
