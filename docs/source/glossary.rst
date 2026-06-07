Glossary
========

.. glossary::


   Heartbeat
      The heartbeat defines the rhythm in which bullets are emitted over a
      given time window.  For example, every 10 seconds give me 3 emits at
      seconds 1-3, and another one at second 5.

      It's just a trigger that now is the time to emit bullets.

   Ring
      A Ring describes a shape from which bullets are emitted.  The only shape
      provided is an actual ring, which can cover single points, full rings,
      and partial rings/arcs.

   BulletSource
      The BulletSource is the actual engine part.  It checks the heartbeat if
      it's time for an emit.  Then it fetches coordinates from the Ring, and
      finally runs user provided callbacks to create the actual bullet
      objects.

   POMS
      **P**osition, **O**rientation, **M**omentum, **S**pin
      An object holding dynamics for a bullet or emitter
