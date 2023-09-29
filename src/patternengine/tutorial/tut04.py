import glm
import pygame
import patternengine as pe

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
                   image, bullet_speed, world, group, factory_momentum):
    momentum *= bullet_speed

    poms = pe.POMS(position, 0, momentum, 0)
    bullet = pe.Bullet(image, poms, group)

    bullet.mutators.add(pe.MomentumMutator(bullet))
    bullet.mutators.add(pe.WorldMutator(bullet, world))

    return bullet


def create_pattern(anchor, bullet_speed, group):
    image = pe.bullets.merge(pe.bullets.CIRCLES['medium-ring-danmaku-magenta'](),
                             pe.bullets.CORES['medium-danmaku-magenta']())

    the_sprite_factory = partial(sprite_factory,
                                 image=image,
                                 bullet_speed=150,
                                 world=SCREEN.inflate(64, 64),
                                 group=group)

    ring = pe.Ring(radius=50, steps=8)
    heartbeat = pe.Heartbeat(duration=2, pattern='###...##...#...##...')
    bullet_source = pe.BulletSource(bullets=8, ring=ring, heartbeat=heartbeat)

    poms = pe.POMS(position=anchor)
    factory = pe.Factory(bullet_source, the_sprite_factory, poms=poms)
    factory.mutators.add(pe.MomentumMutator(factory))

    return factory


group = pygame.sprite.Group()
factory = create_pattern(anchor=SCREEN.center,
                         bullet_speed=150,
                         group=group)


running = True
while running:
    dt = min(clock.tick(FPS) / 1000.0, DT_MAX)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            raise SystemExit
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                raise SystemExit

    factory.update(dt)

    screen.fill('black')
    group.update(dt)
    group.draw(screen)

    pygame.display.flip()

    runtime = pygame.time.get_ticks() / 1000
    fps = clock.get_fps()
    sprites = len(group)
    pygame.display.set_caption(f'{TITLE} - {runtime=:.2f}  {fps=:.2f}  {sprites=}')

pygame.quit()
