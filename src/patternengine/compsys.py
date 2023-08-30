"""Some optional helper systems for use with `tinyecs`"""
import tinyecs as ecs


def bullet_source_rotate_system(dt, eid, bullet_source, angular_momentum):
    """Control the `aim` of a `BulletSource` with a `LerpThing`

    To aim an arc in a `BulletSource`, pass a `LerpThing` with minimum and
    maximum angle, the duration of the swing, and optionally its repeat
    pattern and easing.

    This system applies the angular momentum component to the `aim` attribute
    of the `bullet_source` component.

    Parameters
    ----------
    bullet_source: patternengine.BulletSource
        The `BulletSource` component to control

    angular_momentum:
        The `LerpThing` to control the angle over time.

    Returns
    -------
    None

    """
    bullet_source.aim = angular_momentum()


def bullet_source_system(dt, eid, bullet_source, bullet_factory, position):
    """Launch bullets using a factory.

    This system gets bullet coordinates and speeds from the `bullet_source`
    and passes these to the `bullet_factory` to actually create the game
    objects.

    Note
    ----
    This system loops over the `bullet_source` as long as it returns items.
    So an infinite source without any time interval, that always returns
    `True`, will generate an endless loop and result in your computer running
    out of memory.

    It's the responsibility of the author to make sure, this doesn't happen.

    Parameters
    ----------
    bullet_source: patternengine.BulletSource
        The `BulletSource` component to trigger the emits.

    bullet_factory: Callable[[pygame.Vector2, pygame.Vector2] -> hashable
        The `bullet_factory` is a function that receives `position` and
        `momentum` as `Vector2` and returns the entity id as result.

    Returns
    -------
    None

    """
    for offset, momentum in next(bullet_source):
        bullet_factory(position + offset, momentum)


def aim_ring_system(dt, eid, bullet_source, position, target):
    """A system to aim a bullet source towards a target entity.

    The target is expected to be another entity in the system that also has a
    `position` component.

    This system will then set the `aim` the arc of the `bullet_source`s Ring
    towarts that target.

    Parameters
    ----------
    bullet_source: patternengine.BulletSource
        The `BulletSource` component to control

    position: Vector2
        The position component of the emitter entity to calculate the vector
        towards the target.

    target: hashable
        The eid of the target entity.  This is expected to have a `position`
        component to calculate the aim vector.

        Note
        ----
        If the target has already been removed, or it doesn't have a
        `position` component, this system simply returns.

    Returns
    -------
    None

    """
    if not ecs.has(target):
        return

    try:
        tpos = ecs.comp_of_eid(target, 'position')
    except ecs.UnknownComponentError:
        return

    v = tpos - position
    bullet_source.ring.aim = v.as_polar()[1]
