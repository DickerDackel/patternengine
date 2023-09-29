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
    image = pe.bullets.merge(pe.bullets.SQUARES['tiny-ring-danmaku-blue'](),
                             pe.bullets.CORES['tiny-lightblue']())

    the_sprite_factory = partial(sprite_factory,
                                 image=image,
                                 bullet_speed=150,
                                 world=SCREEN.inflate(64, 64),
                                 group=group,
                                 spin=90)

    bullets = 8
    ring = pe.Ring(radius=0, steps=bullets)
    heartbeat = pe.Heartbeat(duration=2, pattern='#')
    bullet_source = pe.BulletSource(bullets=bullets, ring=ring, heartbeat=heartbeat)
    stack = pe.Stack(bullet_source, height=3, gain=1.15)
    fan = pe.Fan(stack, arc=15, steps=3)

    poms = pe.POMS(position=anchor)
    factory = pe.Factory(fan, the_sprite_factory, poms=poms)

    factory.mutators.add(pe.MomentumMutator(factory))

    return factory


group = pygame.sprite.Group()
factories = [
    pattern01(anchor=SCREEN.center, bullet_speed=100, group=group)
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

    pygame.display.flip()

    runtime = pygame.time.get_ticks() / 1000
    fps = clock.get_fps()
    sprites = len(group)
    pygame.display.set_caption(f'{TITLE} - {runtime=:.2f}  {fps=:.2f}  {sprites=}')

pygame.quit()
