from collections.abc import Iterator, Sequence
from itertools import chain, cycle
from random import random
from typing import Callable, Protocol

import glm

from glm import vec2


type Emit = tuple[vec2, vec2]
type Vector = glm.vec2 | Sequence[float, float]


class EmitSource(Protocol):
    def __init__(*args, **kwargs) -> Iterator[Emit]:
        ...
class Ring:
    """A generator for emit coordinates.

    :param radius: The radius of the ring.  Set to ``0`` to emit from the center.
    :param segments: The number of segments the circle (or arc) is divided into.
    :param aim: For arcs, this gives the direction the center of the arc is pointing towards in degrees.
    :param width: The number of degrees the ring covers.  Default is 360, which gives a full circle.  To only create a 1/4 arc, set this to 90.  Note that start and end position will be included.
    :param steps: A pattern that describes which segment to emit.  *On* is
        represented by ``#``, all other characters are considered *off*.
    :param randomize: If ``randomize`` is set, ``steps`` is ignored and coordinates are chosen randomly from the ring.
    :param rng: Alternative random function

    The rng is assumed to have the following prototype::

        def rng() -> float  # in the range 0 - 1

    .. note:: "Rings" are not intended to be used directly, but if you do, you
       get values out of it using ``next(ring)``.
    """

    def __init__(self,
                 radius: float,
                 segments: int,
                 aim: float = 0,
                 width: float = 360,
                 randomize: bool = False,
                 steps: str = '#',
                 jitter: float = 0) -> None:
        self.radius = radius
        self.segments = segments
        self.aim = aim
        self.width = width
        self.randomize = randomize
        self.steps = cycle(steps)
        self.jitter = jitter

        self.arc = _arc_cycle(self.width, self.segments)

    def __iter__(self) -> Iterator[Emit]:
        return self

    def __next__(self) -> Emit | None:
        """Return the next position and momentum"""

        if self.randomize:
            phi = random() * self.width - self.width / 2
        else:
            phi = next(self.arc)
            if next(self.steps) != '#':
                return None

        angle = phi + self.aim

        if self.jitter:
            jitter = random() * self.jitter - self.jitter / 2
            angle += jitter
        rad = glm.radians(angle)
        v = glm.rotate(vec2(1, 0), rad)

        return v * self.radius, v


class Disk:
    """A generator for emits from a circular area.

    :param radius: The radius of the emit disk
    :param rng: Alternative random function

    The position will be a random point within the defined disk.  The
    momentum will be a normalized vector from the origin ``(0, 0)`` towards
    that position.

    The rng is assumed to have the following prototype::

        def rng(radius: float) -> vec2  # returns normalized vector

    .. note:: Use :func:`patternengine.Ring` if you want control over the
       direction and arc of the emitted particles.

    .. note:: "Rings" are not intended to be used directly, but if you do, you
       get values out of it using ``next(ring)``.
    """

    def __init__(self,
                 radius: float = 1,
                 rng: Callable[[float], vec2] = glm.diskRand) -> Iterator[Emit]:
        self.radius = radius
        self.rng = rng

    def __next__(self):
        """Return the next position and momentum"""

        pos = self.rng(self.radius)
        momentum = glm.normalize(pos)

        return pos, momentum


def _segmentalize_range(length: float, segments: int) -> float:
    """Return a cycle over ``segments`` points on range 0-1."""

    step = 1 / (segments - 1) if segments > 1 else 0

    return [i * step for i in range(segments)]


class Line:
    """A generator for emits along a line.

    :param angle: The angle of the emit line
    :param length: The length of the emit line
    :param steps: The number of points on the emit line (including the end point)
    :param anchor: The anchor point of the emit line (default=0.5, middle)
    :param randomize: Return random positions on the emit line istead of fixed steps
    :param rng: Alternative random function
    :param emit_angle: The direction of the momentum
    :param repeat: 0: cycle, 1: bounce back & forth

    The rng is assumed to have the following prototype::

        def rng() -> float  # in the range 0 - 1

    .. note:: "Rings" are not intended to be used directly, but if you do, you
       get values out of it using ``next(ring)``.
    """

    def __init__(self,
                 angle: float = 0,
                 length: float = 1,
                 steps: int = 2,
                 anchor: float = 0.5,
                 randomize: bool = False,
                 rng: Callable = random,
                 emit_angle: float = 90,
                 repeat: int = 0) -> Iterator[Emit]:
        self.angle = angle
        self.length = length
        self.anchor = anchor
        self.randomize = randomize
        self.rng = rng
        self.emit_angle = emit_angle

        line_steps = _segmentalize_range(self.length, steps)
        if repeat == 0:
            self.cycle = cycle(line_steps)
        elif repeat == 1:
            self.cycle = cycle(chain(line_steps, line_steps[-2:0:-1]))

    def __next__(self) -> Emit:
        """Return the next position and momentum"""

        # Don't cache calculated values, since angle, anchor, length, and
        # emit_angle can change during runtime!
        rad = glm.radians(self.angle)
        emit_rad = glm.radians(self.emit_angle)

        direction = glm.rotate(vec2(1, 0), rad)
        momentum = glm.rotate(direction, emit_rad)

        start = -direction * self.length * self.anchor
        if self.randomize:
            pos = start + self.length * direction * self.rng()
        else:
            pos = start + self.length * direction * next(self.cycle)

        return pos, momentum


class Point:
    """A generator for emits from a single point.

    :param angle: The angle towards which to emit bullets, random if ``None``

    Use a ``Ring`` with radius 0 if you need more complex control over the
    emit direction.

    .. note:: "Rings" are not intended to be used directly, but if you do, you
       get values out of it using ``next(ring)``.
    """

    def __init__(self, angle: float | None = None):
        self.angle = angle

    def __next__(self) -> Emit:
        """Return the next position and momentum"""

        momentum = glm.circularRand(1) if self.angle is None else glm.rotate(vec2(1, 0), glm.radians(self.angle))

        return vec2(0, 0), momentum


class Rectangle:
    """A generator for emits from a rectangular area.

    :param width: The width of the rectangle
    :param height: The height of the rectangle
    :param rng: Alternative random function

    The rectangle will always have its center at ``(0, 0)``.

    The rng is assumed to have the following prototype::

        def rng() -> float  # in the range 0 - 1

    .. note:: "Rings" are not intended to be used directly, but if you do, you
       get values out of it using ``next(ring)``.
    """

    def __init__(self,
                 width: float,
                 height: float,
                 rng: Callable = random) -> Iterator[Emit]:
        self.width = width
        self.height = height
        self.rng = rng

    def __next__(self):
        """Return the next position and momentum"""

        pos = vec2(self.rng() * self.width - self.width / 2,
                   self.rng() * self.height - self.height / 2)
        angle = glm.atan2(pos.y, pos.x)
        momentum = glm.rotate(vec2(1, 0), angle)

        return pos, momentum


def _arc_cycle(arc: float, segments: int) -> float:
    """Return a cycle over `segments` within `arc`."""

    step = 1 / segments if (arc == 360 or segments == 1) else 1 / (segments - 1)

    recenter = 0 if arc == 360 else arc / 2
    return cycle([step * arc * i - recenter for i in range(segments)])
