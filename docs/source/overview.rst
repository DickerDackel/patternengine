Overview
========

patternengine is a library to create bullet hell style bullet patterns for
:term:`shmups`.

Since these patterns can become quite complex, the responsibilities for
emitting bullets is separate into different parts:

* :term:`Heartbeat`
* :term:`Ring`
* :term:`BulletSource`


Heartbeat
---------

The heartbeat is responsible for telling when an emit needs to take place. In
it's core, it's an infinite generator of booleans depending on time and a
provided pattern.

To instantiate a :class:`patternengine.Heartbeat`, you provide 2 arguments:

* duration - the number of seconds a full cycle of the heartbeat will take.
* pattern - A string with on (``#``)/off (``.``) symbols that is mapped onto
  the given duration.

The *on* character is ``#``, every other character is *off*.  I tend to use
``.`` since easier to count than a space character, but see the
:ref:`note <pattern-chars>` below.

For the most trivial case of 1 bullet every n seconds, the ``duration`` is
just the number of seconds between bullets, and the ``pattern`` has only a
single on value::

   heartbeat = Heartbeat(1, '#')

It gets more interesting, when bullets are to be emittet in irregular chunks
over a duration::

   heartbeat = Heartbeat(10, '###.#.....')

Here a single cycle takes 10 seconds.  On seconds 1, 2, 3 and 5, the heartbeat
will generate a ``True`` value, all other times it will return ``False``

.. _pattern-chars:
.. note:: The characters in the ``pattern`` Doesn't need to match the number
   of seconds.  ``Heartbeat(3, '#.#.#.#')`` is completely valid.  The 7 on/off
   states will be distributed over 3 seconds.

You can see the :class:`Heartbeat` in action directly in the interpreter.  Try
this::

   from time import sleep
   from patternengine import Heartbeat

   for emit in Heartbeat(3, '##.'):
       print(emit, end=' ', flush=True)
       sleep(1)

   # --> True True False True True False True True False ...

Since *all* characters except the ``#`` are interpreted as *off*, you can use
digits to make it easier to hit the proper column, especially when creating a
lot of patterns::

   # using a template of '0123456789'
   hb_blue = Heartbeat(5, '#1#3##6789')
   hb_red  = Heartbeat(5, '0#2#45#789')


Ring
----

While the :class:`Heartbeat` is responsible for signalling *when* to emit, the
Ring is responsible for *where* bullets will be emitted.

Like the ``Heartbeat``, the :class:`Ring` is an infinite generator.  Every
time it it queried, it returns a list of `(position, momentum)` tuples.

.. note:: For quite some time, the ``Ring`` was the only class to create
   coordinates.  The list has grown by now, but the term ``Ring`` is still
   used for all classes that create ``(position, momentum)`` tuples.  More
   shapes are described further below...

.. important:: The coordinates returned by the ring are positioned around the
   origin ``(0, 0)``.  The patternengine can't make any assumptions about how
   you manage your entity coordinates in your project.  So it's your
   responsibility to add the actual position of the emitter to the returned
   coordinates.

The returned ``momentum`` is a normalized vector pointing outwards from the
ring's center.

To instantiate a Ring in the most basic configuration, you give it a radius
and a number of steps to split into.  See :class:`patternengine.Ring` for
full documentation.

A basic gun that fires into a static direction would be created from a
``Ring`` with ``radius=0`` and ``steps=1``::

   ring = Ring(0, 1)

By segmenting the ring e.g. into 4 parts, the ring will forever cycle through
the positions 0, 90, 180, 270 degrees.
   ring = Ring(50, 4)

To make things more interesting, the active steps of the ring can be configured.

   ring = Ring(50, 4, '##_')

The ``steps`` string works the same as the ``pattern`` from the ``Heartbeat``
above.  A ``#`` sign means an emit, every other character will make the ring
return None.  The ``steps`` cycle infinitely.

If ``steps`` aligns with ``segments``, e.g. setting it ton ``'#'`` (the
default) or ``segments * '#'``, the pattern is predictable and follows the
segments of the ring.

If the length of ``steps`` differs from the number of segments and contains
*off* symbols, like above, the pattern becomes more complex.  The cycling
through the segments and the cycling over the steps no longer line up.

Instead of a full circle, the ``Ring`` can be configured to return coordinates
from an arc.  This center of the arc points straight to the right by default.

If you want to point the arc to a different direction, pass the ``aim``
parameter to the ``Ring``, which rotates the the direction counter clockwise
by the given degrees.

Passing a ``width`` will define the span of the ring in degrees.

So a 3 segment 90 degree arc of radius 100, pointing straight down can be
created by::

   ring = Ring(100, 3, aim=-90, width=90)

and it will give you the following coordinates in repeat::

   (-70.7107, -70.7107)
   (0, -100)
   (70.7107, 70.7107)

To have a bullet pattern that is moving back and forth instead of covering the
range of the arc and then start from the beginning, see how this can be done
with the ``BulletSource`` below better.

BulletSource
------------

The :class:`Bulletsource` finally brings the `Heartbeat` and the `Ring`
together.

It takes 3 parameters to instantiate the ``BulletSource``.

* The number of bullets to emit in a single event
* A ``Ring`` instance
* A ``Heartbeat`` instance
* Optionally an ``aim`` angle in degrees

Like the other two, the BulletSource is a generator.  Every time it is queried, it

#. Checks if the time based heartbeat signals an emit.  If it does...
#. ...it fetches ``bullets`` coordinates from the Ring
#. Finally it returns a list of ``position``/``momentum`` tuples, or ``None``
   if nothing is emitted.

The ``BulletSource`` is your actual interface to the patternengine.  You
usually won't interact with the ``Ring`` or the ``Heartbeat``.

Every time the ``BuleltSource`` is queried, it returns either ``None`` if it's
not the time to emit, or a list of ``(position, momentum)`` tuples.

As noted in the ``BulletSource`` above, an arc can't amit positions that
bounce back and forth.  This can be made possible by instead emitting a
straight line, but then rotating the bullet source.  Since this is a very
specialized function, and all sorts of angle modifications can be imagined,
the ``aim`` is a writable attribute that should be modified by the user during
runtime, e.g. with an external tool like ``pgcooldown.LerpThing``.
