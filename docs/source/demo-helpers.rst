Helpers and the Pattern Demos
=============================

.. danger:: This part of the library is highly experimental and prone to be
   replaced with something completely different.  Also the documentation is
   incomplete.

With the basic concepts covered in :doc:`introduction`, there are a lot of
patterns in bullet hell games, that can't be created just from the result of a
``BulletSource`` alone.

.. important:: All the all the bullet pattern demos have been made with the
   help of these data structures and the functions that work on them, but
   personally I don't use this part of the library anymore, since I'm working
   with ECS instead.

   So have a look at `pe-demo 01` - `pe-demo 06` and the source code, and use
   this at your own risk.

   They are no longer an official part of *patternengine*, consider them
   application code of the demos.

The POMS
--------

Both generated bullets and emitters can be in motion, angled, or spinning.
The :class:`POMS` class is a container for these operations.  ``POMS`` stands
for

- **P**\ osition
- **O**\ rientation
- **M**\ omentum
- **S**\ pin

position
   The position of the bullet or emitter within the game world.

orientation
   The direction the bullet or emitter is "looking towards".

momentum
   The linear direction and speed with wich a bullet or emitter moves.

spin
   The speed with wich a bullet or emitter rotates

This is the corner data structure for all dynamics in the helper functions and
classes.  It comes with :term:`Mutator`s that manipulate it.

The Mutator Stack
-----------------

Mutators are small functions that modify other objects.  E.g. a function that
modifies the speed of an entity.

The :class:`MutatorStack` is the container for these functions, and it comes
with a ``run`` method to apply them.


.. attention:: FIXME To be continued...
