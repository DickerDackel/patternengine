from collections.abc import Generator

import glm

from itertools import cycle

from pgcooldown import Cooldown
from glm import vec2

from patternengine.poms import POMS, MutatorStack
from patternengine.rings import _arc_cycle


class Heartbeat:
    """A generator for emit signals to be used with ``BulletSource``

    :param duration: The duration of a full cycle of emits in seconds.
    :param pattern: A string containing on/off character symbols.  *On* is
        represented by ``#``, all other characters are considered *off*.

    The following will create emit signals on seconds 1, 2, 3, 5, and 9 over a
    10 second interval::

        Heartbeat(10, '###.#...#.')

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
    :param max_emits: An optional hard limit on the number of emits
    :raises StopIteration: When max_emits is given and reached
    """

    def __init__(self, bullets, ring, heartbeat, aim=0, max_emits=0):
        self.bullets = bullets
        self.ring = ring
        self.heartbeat = heartbeat
        self.aim = aim
        self.max_emits = max_emits
        self.emits = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.max_emits and self.emits >= self.max_emits:
            raise StopIteration

        if not next(self.heartbeat):
            return []

        res = []
        remaining = self.max_emits - self.emits if self.max_emits else self.bullets
        for i in range(min(self.bullets, remaining)):
            if self.max_emits and self.emits >= self.max_emits:
                break

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

            self.emits += 1

        return res


class Factory:
    """A bullet pattern factory.

    :param bullet_source: A preconfigured bullet source.  See above.
    :parm sprite_factory: A callback that creates a sprite from a position and momentum vector.
    :param poms: Optional (P)osition, (O)rientation, (M)omentum and (S)pin object for the Factory.

    The `Factory` will take the emit signals from a `BulletSource` and call a
    sprite factory for every emitted bullet.

    The sprite factory will receive a position and a momentum vector from the
    Factory.  By default, the position vector of the Ring will be centered at
    `(0, 0)`.  If the Factory has a POMS attribute (see below), its position
    will be added to the position vector from the `Ring`.

    The momentum vector will be normalized (set to length 0), and needs to be
    scaled up with the required bullet speed by the sprite factory.  If the
    `Factory` has a `POMS` attribute with `orientation`, the momentum vector
    for the bullet will be rotated by that amount.

    If the `Factory` has a `POMS` attribute with momentum, that is passed as
    `factory_momentum` kwarg to the sprite factory.

    To pre-configure a sprite factory, use a partial that feeds in all
    required settings, or write a an appropriate wrapper function.

    Besides a `POMS`, the `Factory` will also accept a list of mutators that
    can modify the `POMS` e.g. move or rotate the Factory across the screen.
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


class Stack:
    """Stack an emitted ring.

    :param bullet_source: The preconfigured bullet source, consisting of a
        ring and a heartbeat. See above.
    :param height: The height of the stack
    :param gain: The factor to upscale the momentum for each level in the
        stack.  The higher the gain, the further the emitted bullets spread
        out along their flight path.

    Pass the `Stack` instance to the `Factory` instead of the `BulletSource`.

    Instead of increasing the emit frequency of a ring, to release a stack of
    bullets, this class can be used.

    It gets one emit from a bullet source and replicates it a given number of
    times.  Since all emitted bullets in a stack would have been the same
    speed and thus be placed exactly on top of each other, a speed gain factor
    is introduced, that scales the momentum of each level in the stack up by a
    small amount.

    This results in a stack of bullets that emit from a single point, but then
    spread out in the direction of their momentum.  See `pe-demo 01` for an
    example.
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

    :param bullet_source: The preconfigured bullet source, consisting of a
        ring and a heartbeat. See above.
    :param arc: The angle width of the fan, centered around the initial bullet position.
    :param segments: The number of segments the fan is split into.

    Instead of increasing the number of bullets per ring emit, bullets can be
    fanned out over an angle.  So this is the "horizontal" counterpart to the
    "vertical" stack.

    It gets one emit from a bullet source and copies it a given number of
    times.  The fan is centered around the initially emitted bullet.  The
    `arc` of the fan is split um into `steps` pieces.

    .. note:: Pass the `Fan` instance to the `Factory` instead of the
        `BulletSource`. A `Stack` can also be fanned out.
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
