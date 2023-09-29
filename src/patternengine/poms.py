"""Manage (P)osition, (O)rientation, (M)omentum, (S)pin of an object.

This module consists of 2 parts, the POMS object, that contains the
orientation and motion data for an object, and the MutatorStack, that holds
functions that manipulate the object using the POMS information.

FIXME
"""


import glm

from abc import ABC, abstractmethod
from pgcooldown import Cooldown
from patternengine.peglm import clamp

__all__ = [
    'POMS',
    'Mutator',
    'AccelerationMutator',
    'AimTargetMutator',
    'AlignWithAccelerationMutator',
    'AlignWithMomentumMutator',
    'AlignWithTargetMutator',
    'BounceMutator',
    'MomentumMutator',
    'SpinMutator',
    'TurnMutator',
    'WorldMutator',
    'LifetimeMutator',
]


class POMS:
    """Container for (P)osition, (O)rientation, (M)omentum, (S)pin.

    This object is used in many classes to manage position and motion.  It's
    used by `Bullet`, `Factory`, `Ring` and `Fan`.

    The class itself doesn't contain any methods, but it provides a defined
    interface for all mutators below.

    Parameters/Attributes
    ----------
    position: vec2 | tuple[float, float]
        The object's position in 2D space

    orientation: float = 0
        The object's orientation in degrees, defaults to 0

    momentum: vec2 | tuple[float, float] = vec2(0, 0)
        The linear momentum (a.k.a. speed) of the object in 2D space

    spin: float = 0
        The angular momentum of the object (a.k.a. rotation speed)
    """
    def __init__(self, position, orientation=0, momentum=None, spin=0, max_speed=0, max_spin=0):
        self.position = glm.vec2(position)
        self.orientation = orientation
        self.momentum = glm.vec2(momentum) if momentum else glm.vec2()
        self.spin = spin
        self.max_speed = max_speed
        self.max_spin = max_spin

    def __repr__(self):
        return f'{__class__}({repr(self.position)}, {self.orientation}, {repr(self.momentum)}, {self.spin})'


class MutatorStack(dict):
    """The mutator stack for an object that has a POMS attribute.

    The MutatorStack is nothing more than a dict that has an additional `run` method.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if args:
            self.add(*args)

    def run(self, *args, **kwargs):
        """Run all mutators with *args, **kwargs passed into them."""
        for m in self.values():
            m(*args, **kwargs)

    def add(self, *args):
        for arg in args:
            if arg is None: continue
            if isinstance(arg, dict):
                self.update(arg)
            elif isinstance(arg, (list, tuple, set)):
                for mutator in arg:
                    self[type(mutator)] = mutator
            else:
                self[type(arg)] = arg


class Mutator(ABC):
    """The base class for mutators.

    Mutators are classes that modify attributes in their parent instance.

    A mutator e.g. in a sprite that has a POMS attribute for position and
    speed, a mutator can be used to add the POMS' momentum vector to the
    position vector every frame.

    The initial version only gets a reference to the parent object in the
    `__init__`.  This is mandatory.  Also calling `super().__init__(parent)`
    is mandatory.  Everything beyond that is responsibility of the derived
    child class.

    Parameters
    ----------
    parent: object
        The object that the mutator will manipulate
    """
    def __init__(self, parent):
        self.parent = parent

    @abstractmethod
    def __call__(self, dt):
        """Run the mutator

        Mutator objects are called with delta time as only parameter.

        Parameters
        ----------
        dt: float
            delta time since last frame in miliseconds

        Returns
        -------
        None
        """
        ...


class MomentumMutator(Mutator):
    """Update a POMS' position attribute by its momentum.

    Parameters
    ----------
    parent: object
        The parent object
    poms: str
        The attribute **name** of the POMS attribute in the parent class

    """
    def __init__(self, parent, poms='poms'):
        super().__init__(parent)
        self.poms = poms

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)

        if poms.max_speed:
            poms.position = poms.position + clamp(poms.momentum, poms.max_speed) * dt
        else:
            poms.position = poms.position + poms.momentum * dt


class SpinMutator(Mutator):
    def __init__(self, parent, poms='poms'):
        super().__init__(parent)
        self.poms = poms

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)
        if poms.max_spin:
            poms.orientation = (poms.orientation + min(poms.spin, poms.max_spin) * dt) % 360
        else:
            poms.orientation = (poms.orientation + poms.spin * dt) % 360


class AlignWithMomentumMutator(Mutator):
    def __init__(self, parent, poms='poms'):
        super().__init__(parent)
        self.poms = poms

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)
        poms.orientation = glm.degrees(glm.atan2(*poms.momentum) - glm.half_pi())


class TurnMutator(Mutator):
    def __init__(self, parent, poms='poms'):
        super().__init__(parent)
        self.poms = poms

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)
        phi = glm.radians(poms.spin)
        max_phi = glm.radians(poms.max_spin)
        if poms.max_spin:
            poms.momentum = glm.rotate(poms.momentum, min(phi, max_phi) * dt)
        else:
            poms.momentum = glm.rotate(poms.momentum, phi * dt)


class AimTargetMutator(Mutator):
    def __init__(self, parent, target, ppoms='poms', tpoms=None):
        super().__init__(parent)
        self.target = target
        self.ppoms = ppoms
        self.tpoms = tpoms if tpoms else ppoms

    def __call__(self, dt):
        ppoms = getattr(self.parent, self.ppoms)
        tpoms = getattr(self.target, self.tpoms)

        p0 = ppoms.position
        p1 = tpoms.position
        v = p1 - p0
        angle = glm.degrees(glm.atan2(v.x, v.y) - glm.half_pi())

        if ppoms.max_spin:
            ppoms.orientation += min(angle, ppoms.max_spin) * dt
        else:
            ppoms.orientation = angle


class AlignWithTargetMutator(Mutator):
    def __init__(self, parent, target, ppoms='poms', tpoms=None):
        super().__init__(parent)
        self.target = target
        self.ppoms = ppoms
        self.tpoms = tpoms if tpoms else ppoms

    def __call__(self, dt):
        if not self.mode: return

        ppoms = getattr(self.parent, self.ppoms)
        tpoms = getattr(self.target, self.tpoms)

        p0 = ppoms.position
        p1 = tpoms.position
        v = p1 - p0
        angle = glm.atan2(*v)

        if ppoms.max_spin:
            ppoms.momentum = glm.rotate(ppoms.momentum,
                                        glm.radians(min(angle, ppoms.max_spin) * dt))
        else:
            ppoms.momentum = glm.rotate(ppoms.momentum, angle * dt)


class AccelerationMutator(Mutator):
    def __init__(self, parent, acceleration, poms='poms'):
        super().__init__(parent)
        self.poms = poms
        self.acceleration = acceleration

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)
        poms.momentum += self.acceleration * dt


class AlignWithAccelerationMutator(Mutator):
    def __init__(self, parent, poms='poms'):
        super().__init__(parent)
        self.poms = poms

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)
        accel = self.parent.mutators[AccelerationMutator].acceleration

        poms.orientation = glm.degrees(glm.atan2(*accel) - glm.half_pi())


class WorldMutator(Mutator):
    def __init__(self, parent, world, poms='poms'):
        super().__init__(parent)
        self.world = world
        self.poms = poms

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)
        if not self.world.collidepoint(poms.position):
            # Remove circular referencing of parent in the mutators
            self.parent.mutators.clear()
            self.parent.kill()


class LifetimeMutator(Mutator):
    def __init__(self, parent, lifetime):
        super().__init__(parent)
        self.lifetime = Cooldown(lifetime)

    def __call__(self, dt):
        if self.lifetime.cold():
            # Remove circular referencing of parent in the mutators
            self.parent.mutator.clear()
            self.parent.kill()


class BounceMutator(Mutator):
    def __init__(self, parent, world):
        super().__init__(parent)
        self.world = world

    def __call__(self, dt):
        position = self.parent.poms.position
        momentum = self.parent.poms.momentum

        if position.x > self.world.right:
            position.x = 2 * self.world.right - position.x
            momentum.x = -momentum.x
        elif position.x < self.world.left:
            position.x = -position.x
            momentum.x = -momentum.x
        if position.y > self.world.bottom:
            position.y = 2 * self.world.bottom - position.y
            momentum.y = -momentum.y
        elif position.y < self.world.top:
            position.y = -position.y
            momentum.y = -momentum.y
