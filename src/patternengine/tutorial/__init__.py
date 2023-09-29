"""patternengine tutorial

# patternengine tutorial

All sources from this tutorial can be found in the paternengine/tutorial
folder.  They all can be run with `pe-tutorial tut<nn>`

## Concepts

This tutorial will guide you through creating your first basic pattern,
introducing the provided tools.

In the world of `patternengine`, there are FIXME parts to a bullet pattern.

### 1. The Ring

This is the object that creates the coordinates at which bullets appear, and
the momentum with which they drift across the screen.

The Ring is not limited to a full circle, an arc of a fixed width in degrees
can be specified, and the number of steps in the ring that can emit bullets.

Note, that the ring does not control how many bullets per emit are generated.
That will be decided by the `BulletSource` further down. The `Ring` is *only*
responsible for creating coordinates.

To create a `Ring` with radius of 100 pixels and 8 emit points (every 45
degrees), create the following instance:

```python
ring = pe.Ring(100, 8)
```

### 2. The heartbeat

While the ring controls the position and direction of bullets, the heartbeat
controls the rhythm in which they are emitted.

That rhythm is controlled by its duration and a string that defines both, the
number of steps this duration is split into, and on which of these steps emits
happen.

To create a Heartbeat over 5 seconds, that will emit bullets on seconds 0 and
2, with no emits at seconds 1, 3 and 4, create this instance:

```python
heartbeat = pe.Heartbeat(5, '#.#..')
```

The '#' will be the sign to emit bullets.  Every other character will mean a
gap.  `.` are easier to read, but digits or spaces are valid as well.


### 3. The BulletSource

The BulletSource is a generator class that combines the Ring with the
Heartbeat.

When called with `next(bullet_source)`, it will return a list of `(position,
momentum)` tuples for all the bullets that need to be created in the current
frame.

The `BulletSource` is not used directly.  The Factory will do that for us.

### 4. The Factory

This object combines the bullet source and the sprite factory.  It can also
have its own position on screen and also a momentum, all of which influences
the position and momentum of the bullets that will be emitted.

The factory provides an update method that accepts deltatime.  On every frame,
if the heartbeat confirms an emit, the pending bullet coordinantes with their
momentum are fetched from the bullet sourcee and passed into the sprite
factory one by one.

### 5. the sprite factory

This is *not* a ready made component of the patternengine.  Instead it's a
function or class that needs to be provided by the user, since patternengine
doesn't make assumptions about the framework or plattform the application is
running on.

As of now, patternengine comes with a predefined set of bullet images, and a
flexible bullet sprite class based on pygame-ce.

But the patternengine itself is completely platform independend, so in the
future, additional modules for pyglet and probably raylib will be provided as
well.

### Putting it together:

All of these components will be discussed in more detail during the tutorial.

It's easiest, to create all these elements within a function that in the end
returns a fully configured instance of the `Factory`.

The `update` of that instance then needs to be called in every frame of the
game loop over the lifetime of the Factory (e.g. until the enemy emitting the
pattern is destroyed).


## Putting it to use.

Let me restate: patternengine is not tied to pygame.  It's a generic emitter
system.  But since we want to see bullet patterns at work, this tutorial is using
pygame-ce.

### Tutorial 0

`pe-tutorial tut00`

A basic pygame game loop without any sprites.  It's a black screen, ESC will
end the program.

### Tutorial 1

`pe-tutorial tut01`

#### Imports

Since the name is rather long, feel free to import the patternengine package
under the shortcut namespace `pe`.

Additionally, patternengine uses pyglm for vector math.  While e.g. pygame
comes with the powerful `Vector2` class, as discussed above, to avoid
conflicts with other frameworks, patternengine uses the platform independend
and fast pyglm is used instead.  It has equal capabilities but will not
interfere with any game framework that might be used instead of pygame.

```python
import glm
import pygame
import patternengine as pe
```

#### Sprite Factory

While the sprite factory was the last element in the component list above, we
start with it, so we see something on the screen as early as possible.

```python
clock = pygame.time.Clock()

group = pygame.sprite.Group()


def sprite_factory(position, momentum, group):
    sprite = pygame.sprite.Sprite(group)
    sprite.image = pe.bullets.merge(pe.bullets.CIRCLES['medium-ring-danmaku-magenta'](),
                                    pe.bullets.CORES['medium-danmaku-magenta']())
    sprite.rect = sprite.image.get_rect(center=position.xy)
    return sprite


sprite_factory(glm.vec2(SCREEN.center), glm.vec2(), group)

running = True
while running:
```

Note, while patternengine comes with a powerful bullet sprite class, in this
first instance we don't even create a subclass of pygame.sprite.Sprite.

The sprite_factory is nothing more than a function that receives a position
and an (optional) momentum.  If that function then creates an ECS entity or a
pygame sprite, or whatever else lies completely in the hands of the developer.

In our case, we create a pygame sprite and put it into a pygame sprite group.

The sprite shape we create is one that comes bundled with patternengine.  Run
`demo 00` to see a list of all available shapes and sizes.  They are also
documented in their module `patternengine.bullets`.

In our case, our bullet consists of a brignt core image combined with a
colored ring around that core.

The `pe.bullets.merge` function will combine these two sprite components onto
a single image.

**Note** that this is a relatively expensive operation.  In a real application,
all bullet types should be pre-generated once and provided to the sprite
factories as needed, instead of recreating the bullet image again and again.

Sprite groups in pygame have the big advantage, that you don't need to keep
track of single sprite instances.  A group has an `update` method that then
calls the update method of every sprite within that group with the same
parameters the group.update received.  In our case, that's deltatime.

Note: Since basic game development is not the scope of this tutorial.  To
learn more about the concept of deltatime, read chapters 9 and 10 of

[Game Programming Patterns](https://gameprogrammingpatterns.com/contents.html)

In the game loop, the group's `update` and `draw` functions are called.  The
sprite will appear in the center of the screen.

### Tutorial 2

`pe-tutorial tut02`

Sadly, we can't continue with baby steps, since the `Factory` requires a
`BulletSource`, which requires a `Ring` and a `Heartbeat`.

So we need to create all three at once, and we will also make changes in the
`sprite_factory` to make actual use of the `Factory`, and let us benefit from
the Mutator system to control the dynamics of the bullet.

First, let's create the `Factory`.  Directly below the `sprite_factory`,
create the `ring`, create the `heartbeat`, combine both into a
`bullet_source`, then put this together with the `sprite_factory` into the
`pe.Factory`.


```python
ring = pe.Ring(radius=0, steps=1)
heartbeat = pe.Heartbeat(duration=1, pattern='#')
bullet_source = pe.BulletSource(bullets=1, ring=ring, heartbeat=heartbeat)
factory = pe.Factory(bullet_source, sprite_factory)
```

At 0 degrees, the `Ring` aims directly to the right.  A ring with a radius of
0 will emit from a single center point.  A step of 1 means, only a single
sprite is emitted.

The `heartbeat` has a total duration of 1 second.  Within that one second, it
will create a single emit '#'.

The `Factory` will call the `bullet_source` every frame, and repeatedly, after
1 second, interval, the heartbeat will allow fetching bullets from the ring.
The `bullet_source` is configured to fetch 1 single bullet.

For every bullet the `bullet_source` returns to the `factory`, the `factory`
will call the `sprite_factory` with the `position` and `momentum` as defined
by the `ring`.

The `sprite_factory` will then create a corresponding bullet object.

The `position` will be anchored at `(0, 0)`, so for this step in the tutorial,
we hard wire the center of the screen as anchor for that position.

The `momentum` vector is normalized (which means, it's length is 1).  It needs
to be multiplied by the actual speed we want the bullet to have.

So here's the updated `sprite_factory` with a few explanations missing:

```python
def sprite_factory(position, momentum, *args, **kwargs):
    anchor = glm.vec2(SCREEN.center)
    bullet_speed = 150
    world = SCREEN.inflate(64, 64)

    image = pe.bullets.merge(pe.bullets.CIRCLES['medium-ring-danmaku-magenta'](),
                             pe.bullets.CORES['medium-danmaku-magenta']())
    position += anchor
    momentum *= bullet_speed

    poms = pe.POMS(position, 0, momentum, 0)
    bullet = pe.Bullet(image, poms, group)

    bullet.mutator.add(pe.MomentumMutator(bullet))
    bullet.mutator.add(pe.WorldMutator(bullet, world))

    return bullet
```

The new `sprite_factory` uses the `Bullet` sprite class that comes with
patternengine.  The `Bullet` is subclassed from `pygame.sprite.Sprite`, so the
known mechanics of `bullet.image` and `bullet.rect` as well as putting a
bullet into a sprite group, are unchanged.

But `pe.Bullet` introduces 2 new concepts.

1. the POMS, short for (P)osition, (O)rientation, (M)omemtum, (S)pin
2. Mutators

While normal sprites often tend to have a large amount of parameters,
controlling position, motion, rotation, ... of a sprite, the Bullet outsources
this into the POMS object.

The POMS contains the parameters that define position and movement of the
sprite in the world

Mutators are plugins that modify these parameters.

Since mutators work on data of their parent class, they need to be given that
as a reference.  Thus mutators cannot be added when creating the Bullet
object, but need to be put in place once the `Bullet` instance is created.

In this example, we make use of the simple MomentumMutator.  When called, it
fetches the poms attribute from the parent (the Bullet) instance.  It then
adds `poms.momentum * dt` to `poms.position`.

The `bullet.update(dt)` function will be called when calling
`group.update(dt)`, and there, the `poms.position` will be copied to the
`bullet.rect.center`, giving the sprite its position on screen.

There is a growing catalog of mutators.  Look into the documentation of
`patternengine.poms` for a list.

We use an additional mutator here to remove bullets that have moved outside
the screen rectangle.

The `pe.WorldMutator` will check, if the Bullet's center point is still within
the bounds of the world rect that needs to be passed to the init of the
mutator.

Once the sprite has left the visible area, `pe.WorldMutator` will call the
`bullet`s `kill()` method which removes it from all sprite groups.
Additionally, it will also clear the mutator stack, so that no circular
references are left that keep the `bullet` from being garbage collected.

Running `pe-tutorial tut02`, a magenta bullet is created at the center of the
screen every second.  It travels to the right at a speed of 150px/s and it
will be removed from the system after it has left the screen.

### Tutorial 03

`pe-tutorial tut03`

Let's refactor a few things:

1. Get rid of using the global `group` and the hard wired bullet speed,
   anchor, world rect

2. place the creation of the `pe.Factory` and its configuration objects into a
   function.

```python
def sprite_factory(position, momentum, *,
                   image, bullet_speed, world, group, factory_momentum):
    momentum *= bullet_speed

    poms = pe.POMS(position, 0, momentum, 0)
    bullet = pe.Bullet(image, poms, group)

    bullet.mutator.add(pe.MomentumMutator(bullet))
    bullet.mutator.add(pe.WorldMutator(bullet, world))

    return bullet
```

But how do we get all these parameters into that function, when the
`pe.Factory` only passes `position` and `momentum`?

By setting the function up as a `partial`.  Using `functools.partial` creates
a wrapped function of `sprite_factory` that has all required parameters
already filled out.  When the `pe.Factory` runs `sprite_factory(position,
momentum)`, and we give it our partial instead of the initial `sprite_factory`
function, all these parameters are filled out already.

Here is the new `pattern01` function in which we wrap the partial for the
`sprite_factory` and the creation of the `pe.Factory`.

```python
def pattern01(anchor, bullet_speed, group):
    image = pe.bullets.merge(pe.bullets.CIRCLES['medium-ring-danmaku-magenta'](),
                             pe.bullets.CORES['medium-danmaku-magenta']())

    the_sprite_factory = partial(sprite_factory,
                                 image=image,
                                 bullet_speed=150,
                                 world=SCREEN.inflate(64, 64),
                                 group=group)

    ring = pe.Ring(radius=0, steps=1)
    heartbeat = pe.Heartbeat(duration=1, pattern='#')
    bullet_source = pe.BulletSource(bullets=1, ring=ring, heartbeat=heartbeat)
    poms = pe.POMS(position=anchor)
    return pe.Factory(bullet_source, the_sprite_factory, poms=poms)


group = pygame.sprite.Group()
factory = pattern01(anchor=SCREEN.center, bullet_speed=150, group=group)
```

These changes give us still the same result of 1 bullet flying to the right,
but we got rid of hard wired values or the use of globals within functions.


### Tutorial 04

`pe-tutorial tut04`

From here on, now that the basic mechanics are explained, we'll expand on our pattern.

    1. Increase the radius of the ring
    2. Increase the steps in the ring to 8 (every 45 degrees)
    3. Let Heartbeat create a `3 - 2 - 1 - 2 -` pattern with a cycle duration
       of 2 seconds

```python
    ring = pe.Ring(radius=50, steps=8)
    heartbeat = pe.Heartbeat(duration=2, pattern='###...##...#...##...')
    bullet_source = pe.BulletSource(bullets=8, ring=ring,mutatorsheartbeat=heartbeat)
    poms = pe.POMS(position=anchor)
    return pe.Factory(bullet_source, the_sprite_factory, poms=poms)
```


### Tutorial 05

`pe-tutorial tut05`

Add a second pattern

    1. A ring with radius 50 and 8 steps emitting...
    2. ...a spinning blue square with a bright blue core...
    3. ...in stacks of 3
    4. with the `pe.Factory` spinning at 5 seconds per full rotation

`Stack` is a new concept.  Stacks and Fans are multiplicators of bullets from
a `BulletSource`.

A stack is defined by a `BulletSource`, a `height` and a `gain` which is a
multiplicator for the speed of the emitted bullets.

In a stack with a height of 3, each bullet generated by the `BulletSource` is
copied into 3 versions.  The momentum of the "lowest" bullet is unchanged.
The momentum of the next bullet is multiplied by the `gain`, and the bullet
after that is multiplied by 2 times the gain.

This way, although all bullets have the same origin and emit time, they drift
apart along their direction of momentum over the time of their life, and so
they build a `Stack` of bullets after a second.

A `Fan` does a similar copy of bullets, but instead of scaling up their
momentum, their launch position is fanned out on an arc, creating e.g. 3
bullets side by side instead of one.

Fans and Stacks are stackable.  So you can create a Fan of a Stack.  See tut06
for that.

```python
def pattern02(anchor, bullet_speed, group):
    image = pe.bullets.merge(pe.bullets.SQUARES['tiny-ring-danmaku-blue'](),
                             pe.bullets.CORES['tiny-lightblue']())

    the_sprite_factory = partial(sprite_factory,
                                 image=image,
                                 bullet_speed=150,
                                 world=SCREEN.inflate(64, 64),
                                 group=group,
                                 spin=90)

    bullets = 8
    ring = pe.Ring(radius=50, steps=bullets, aim=5)
    heartbeat = pe.Heartbeat(duration=0.3, pattern='##')
    bullet_source = pe.BulletSource(bullets=bullets, ring=ring, heartbeat=heartbeat)
    stack = pe.Stack(bullet_source, height=3, gain=1.1)

    poms = pe.POMS(position=anchor, spin=360 / 5)
    factory = pe.Factory(stack, the_sprite_factory, poms=poms)

    factory.mutators.add(pe.MomentumMutator(factory))
    factory.mutators.add(pe.SpinMutator(factory))

    return factory
```

Instantiate both, the old pattern and the new one into a list for easier
management.

```python
group = pygame.sprite.Group()

factories = [
    pattern01(anchor=SCREEN.center, bullet_speed=150, group=group),
    pattern02(anchor=SCREEN.center, bullet_speed=100, group=group)
]
```

And run all of the generated patterns in the game loop:

```python

    for f in factories:
        f.update(dt)

    screen.fill('black')
    group.update(dt)
    group.draw(screen)
```

### Tutorial 06

`pe-tutorial tut06`

Create a Fan from pattern02 of tutorial 5

Line the `Stack`, that gets the `BulletSource` as input, the `Fan` now gets
the `Stack` as input.  If you don't need a stack, of course the `BulletSource`
will also work as input for the `Fan`.

```python
    bullets = 8
    ring = pe.Ring(radius=0, steps=bullets)
    heartbeat = pe.Heartbeat(duration=2, pattern='#')
    bullet_source = pe.BulletSource(bullets=bullets, ring=ring, heartbeat=heartbeat)
    stack = pe.Stack(bullet_source, height=3, gain=1.15)
    fan = pe.Fan(stack, arc=15, steps=3)

    poms = pe.POMS(position=anchor)
    factory = pe.Factory(fan, the_sprite_factory, poms=poms)

    factory.mutators.add(pe.MomentumMutator(factory))
```

This will create 8 blocks (every 45 degrees on a full circle) of 3x3 bullets
every 2 seconds.

### Tutorial 07

`pe-tutorial tut07`

Note, that there is a big difference between stacking bullets by means of the
`Stack` or by the `Heartbeat`.

The stack clones one bullet into multiple copies with different behaviour, but
they all drift in the same direction.

When stacking bullets with the `Heartbeat`, these are separate bullets created
by separate events.  So if your bullet source rotates, a `Stack` will have
them all at the same angle, but when stacked by the heartbeat, time has passed
between two emits, and the bullet source has continued to rotate during that
time.

Let's make some changes:

    1. Reduce the number of emit points to 1, so we can clearly see the rotation
    2. Add a LerpThing that lerps from 0 to 360 over 10 seconds as `aim` to the ring
    3. Increase the emit frequency, so the whole behaviour is better visible

```python
    bullets = 1
    ring = pe.Ring(radius=0, steps=bullets, aim=LerpThing(0, 360, 10, repeat=1))
    heartbeat = pe.Heartbeat(duration=1, pattern='##')
```

Now let's copy pattern01 to pattern02 and change a few things:

    1. Make the image a magenta circle
    2. Delete the stack...
    3. ...and recreate it using the heartbeat
    4. rotate the whole factory by 180 degrees so we can compare pattern01 and
       pattern02

```python
def pattern02(anchor, bullet_speed, group):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-magenta'](),
                             pe.bullets.CORES['tiny-lightblue']())

    the_sprite_factory = partial(sprite_factory,
                                 image=image,
                                 bullet_speed=150,
                                 world=SCREEN.inflate(64, 64),
                                 group=group)

    bullets = 1
    ring = pe.Ring(radius=0, steps=bullets, aim=LerpThing(0, 360, 10, repeat=1))
    heartbeat = pe.Heartbeat(duration=1, pattern='###...###...')
    bullet_source = pe.BulletSource(bullets=bullets, ring=ring, heartbeat=heartbeat)
    fan = pe.Fan(bullet_source, arc=15, steps=3)

    poms = pe.POMS(position=anchor, orientation=180)
    factory = pe.Factory(fan, the_sprite_factory, poms=poms)

    factory.mutators.add(pe.MomentumMutator(factory))

    return factory
```

Of course, the 2nd pattern also needs to be created and put into the factories list:

```python
factories = [
    pattern01(anchor=SCREEN.center, bullet_speed=100, group=group),
    pattern02(anchor=SCREEN.center, bullet_speed=100, group=group)
]
```

When running this tutorial, compare the distribution of the magenta bullets
with the blue ones from the `Stack`.  The magenta ones are rotated within the
stacking, while the blue ones all lie on the same radial spike.

### Tutorial 08

`pe-tutorial tut08`

In the two final examples, we'll let the pattern `Factory` drift and bounce
across the screen while emitting bullets.  We'll do this in 2 variants.  In
the first version, the emitted bullets will not inherit the momentum of the
`Factory`.  In the second example, they will.

To keep the `Factory` from drifting off screen, the `poms` module comes with a
`BounceMutator` that checks the position of the factory against a rect, in our
case the `SCREEN` rect.

For better visibility, we leave the number of bullets at 1.  Additionally, the
`Factory`s `poms` gets a momentum vector, an appropriate `MomentumMutator` and
the `BounceMutator` too.


```python
def pattern01(anchor, bullet_speed, group):
    image = pe.bullets.merge(pe.bullets.CIRCLES['small-ring-lightblue'](),
                             pe.bullets.CORES['small-lightblue']())

    the_sprite_factory = partial(sprite_factory,
                                 image=image,
                                 bullet_speed=150,
                                 world=SCREEN.inflate(64, 64),
                                 group=group)

    bullets = 1
    ring = pe.Ring(radius=50, steps=bullets, aim=LerpThing(0, 360, 5, repeat=1))
    heartbeat = pe.Heartbeat(duration=0.1, pattern='#')
    bullet_source = pe.BulletSource(bullets=bullets, ring=ring, heartbeat=heartbeat)

    poms = pe.POMS(position=anchor, momentum=glm.vec2(37, 15) * 5)
    factory = pe.Factory(bullet_source, the_sprite_factory, poms=poms)

    factory.mutators.add(pe.MomentumMutator(factory))
    factory.mutators.add(pe.BounceMutator(factory, world=SCREEN))

    return factory
```

To see where the `Factory` is currently positioned, we hack a red circle at
its place in the main loop:

```python
    group.draw(screen)

    position = factories[0].poms.position
    pygame.draw.circle(screen, 'red', position, 10, width=1)

    pygame.display.flip()
```

When running this, note the interesting patterns that result from the motion
of the emitter and the rotation of the ring.

### Tutorial 08a

`pe-tutorial tut08a`

In this final demonstration, we only make sure, the momentum of a new bullet
also inherits the momentum of the `Factory`

```python
def sprite_factory(position, momentum, *,
                   image, bullet_speed, world, group, factory_momentum,
                   spin=0):
    momentum *= bullet_speed
    if factory_momentum:
        momentum += factory_momentum

    poms = pe.POMS(position, 0, momentum, spin)
```

The change in the resulting pattern is massive and should give you an idea how
small combinations of effects can have suprising impact on the behaviour of
the bullets.

## Conclusion

All basic mechanics have now been demonstrated.  But there is one big
possibility for tweaks left out.

The pattern engine takes care of everything up to the actual launch of the
bullet.  The creation of the bullet is already put into the hands of the
developer, and nobody is forcing you to have a static drifting bullet.

You can create your own bullet classes or make use of an ECS to mutate the
bullet in whatever form you want.  Make them homing missiles, rotate their
momentum over time, let them explode with splash damage into many other
particles, change color, ...

The only limiting factor is your imagination.

With all that said, I hope this library will be useful to create your own shmup or bullet hell.

Suggestions, bug reports, comments are always welcome.

"""

import sys
import os.path
import argparse

from importlib import import_module
from importlib.resources import contents


def main():
    cmdline = argparse.ArgumentParser(description='patternengine tutorial runner')
    cmdline.add_argument('cmd', type=str, nargs='?', default='ls', help='ls or tutorial name')
    opts = cmdline.parse_args(sys.argv[1:])

    match opts.cmd:
        case 'ls':
            print('Available tutorials:')
            tutorials = [os.path.splitext(f)[0] for f in contents('patternengine.tutorial') if not f.startswith('__')]
            for tut in tutorials:
                print(f'    {tut}')

        case _:
            fullname = f'patternengine.tutorial.{opts.cmd}'
            imp = import_module(fullname)
            fkt = getattr(imp, 'main')
            fkt()


if __name__ == '__main__':
    main()
