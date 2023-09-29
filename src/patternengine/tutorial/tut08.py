import glm
import pygame
import patternengine as pe

from pgcooldown import LerpThing
from functools import partial

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
FPS = 60
DT_MAX = 3 / FPS

pygame.init()
pygame.display.set_caption(TITLE)
screen = pygame.display.set_mode(SCREEN.size)
clock = pygame.time.Clock()


def sprite_factory(position, momentum, *,
                   image, bullet_speed, world, group, factory_momentum,
                   spin=0):
    momentum *= bullet_speed

    poms = pe.POMS(position, 0, momentum, spin)
    bullet = pe.Bullet(image, poms, group)

    bullet.mutators.add(pe.MomentumMutator(bullet))
    bullet.mutators.add(pe.WorldMutator(bullet, world))

    if spin: bullet.mutators.add(pe.SpinMutator(bullet))

    return bullet


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


group = pygame.sprite.Group()
factories = [
    pattern01(anchor=SCREEN.center, bullet_speed=75, group=group),
]


running = True
while running:
    dt = min(clock.tick(FPS) / 1000.0, DT_MAX)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            raise SystemExit
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                raise SystemExit

    for f in factories:
        f.update(dt)

    screen.fill('black')
    group.update(dt)
    group.draw(screen)

    position = factories[0].poms.position
    pygame.draw.circle(screen, 'red', position, 10, width=1)

    pygame.display.flip()

    runtime = pygame.time.get_ticks() / 1000
    fps = clock.get_fps()
    sprites = len(group)
    pygame.display.set_caption(f'{TITLE} - {runtime=:.2f}  {fps=:.2f}  {sprites=}')

pygame.quit()


