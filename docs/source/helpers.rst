Helpers
=======

With the basic concepts covered in :doc:`introduction`, there are a lot of
patterns in bullet hell games, that can't be created just from the result of a
``BulletSource`` alone.

Here are some helpers that can assist in creating more complex patterns.

The POMS
--------

Both generated bullets and emitters can be in motion, angled, or spinning.
The :class:`POMS` class is a container for these operations.  ``POMS`` stands
for::
   * **P**osition
   * **O**rientation
   * **M**omentum
   * **S**pin

position
   The position of the bullet or emitter within the game world.

orientation
   The direction the bullet or emitter is "looking towards".

momentum
   The linear direction and speed with wich a bullet or emitter moves.

spin
   The speed with wich a bullet or emitter rotates

This is the corner data structure for all dynamics in the helper functions and
classes.

Mutators
--------


