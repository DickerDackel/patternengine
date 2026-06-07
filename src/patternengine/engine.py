from collections.abc import Generator

import glm

from itertools import cycle
from random import random

from pgcooldown import Cooldown
from glm import vec2

from patternengine.poms import POMS, MutatorStack


__all__ = ['Ring', 'Heartbeat', 'BulletSource', 'Stack', 'Fan', 'Factory']


def _arc_step(phi, segments):
    """Chunk an arc into steps.

    If it's a full circle, don't include both 0 and 360 degrees.
    """
    return 1 / segments if (phi == 360 or segments == 1) else 1 / (segments - 1)


def _arc_cycle(arc, segments):
    """Return a cycle over `steps` within `arc`."""
    step = arc * _arc_step(arc, segments)

    recenter = 0 if arc == 360 else arc / 2
    return cycle([step * i - recenter for i in range(segments)])


class Ring:
    """A generator for emit coordinates.

    :param radius: The radius of the ring.  Set to ``0`` to emit from the center.
    :param segments: The number of segments the circle (or arc) is divided into.
    :param aim: For arcs, this gives the direction the center of the arc is pointing towards in degrees.
    :param width: The number of degrees the ring covers.  Default is 360, which gives a full circle.  To only create a 1/4 arc, set this to 90.  Note that start and end position will be included.
    :param steps: A pattern that describes which segment to emit.  *On* is
        represented by ``#``, all other characters are considered *off*.
    :param randomize: If ``randomize`` is set, ``steps`` is ignored and coordinates are chosen randomly from the ring.
    """

    def __init__(self,
                 radius: float,
                 segments: int,
                 aim: float = 0,
                 width: float = 360,
                 randomize: bool = False,
                 steps: str = '#') -> Generator[tuple[vec2, vec2]]:
        self.radius = radius
        self.segments = segments
        self._aim = aim if callable(aim) else lambda: aim
        self.width = width
        self.randomize = randomize
        self.steps = cycle(steps)

        self.arc = _arc_cycle(self.width, self.segments)

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
            if next(self.steps) != '#':
                return None

        v = vec2(1, 0)
        v = glm.rotate(v, glm.radians(phi + self._aim()))

        return v * self.radius, v


class Heartbeat:
    """A generator for emit signals to be used with ``BulletSource``

    :param duration: The duration of a full cycle of emits in seconds.
    :param pattern: A string containing on/off character symbols.  *On* is
        represented by ``#``, all other characters are considered *off*.

    """

    def __init__(self, duration: float, pattern: str) -> Generator[bool]:
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
    """A generator to emit lists of bullet coordinates.

    :param bullets: Number of bullets to create in a single emit event.
    :param ring: A ``Ring`` instance.
    :param heartbeat: A ``Heartbeat`` instance.
    :param aim: Optional, the rotation angle of the bullet source.
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
    segments: int
        The number of segments the fan is split into.
    """
    def __init__(self, bullet_source, arc, segments):
        self.bullet_source = bullet_source
        self.arc = arc
        self.segments = segments

        self.arc = _arc_cycle(arc, segments)

    def __iter__(self):
        return self

    def __next__(self):
        res = []
        for position, momentum in next(self.bullet_source):
            for degrees, _ in zip(self.arc, range(self.segments)):
                phi = glm.radians(degrees)
                res.append((glm.rotate(position, phi),
                            glm.rotate(momentum, phi)))
        return res


class Factory:
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
