# patternengine
A bullet hell pattern engine

Consult the embedded docs for class descriptions and usage.

Check out [the demo](https://github.com/dickerdackel/patternengine-demo).
Watch [the demo running](https://youtu.be/HtlNjl8-Zd0?si=HTU4GRDHWqJFArzt)

Look into src/patternengine/example.py

Preparation

```py
########################################################################
# Relevant part here
#
# A "ring" of 180 degrees aiming towards the top devided int 18 parts
# A heartbeat over 5 seconds with 4 emits and 4 gaps
# A BulletSource fetching 18 bullets at every heartbeat
#

ring = pe.Ring(100, 18, aim=-90, width=180)
heartbeat = pe.Heartbeat(5, '#.#.#.#.')
emitter = pe.BulletSource(18, ring, heartbeat)

#
########################################################################
```

Later in the game loop

```py

####################################################################
# Relevant part here
#
for bullet in next(emitter):
    Bullet(group,
	   position=bullet[0] + anchor,
	   momentum=bullet[1] * bullet_speed,
	   lifetime=10)
#
####################################################################
```

with Bullet being a simple subclass of pygame.sprite.Sprite

TBC...
