import glm
import pygame
import patternengine as pe

from functools import partial
from pgcooldown import Cooldown, LerpThing
from glm import vec2

from patternengine.bullet import Bullet
from patternengine.poms import POMS, MomentumMutator

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
# SCREEN = pygame.Rect(0, 0, 640, 480)
FPS = 60
DT_MAX = 3 / FPS

BULLET_SPEED = 250


def sprite_factory(position, momentum, anchor, bullet_speed, image, world,
                   group, **kwargs):
    bullet = Bullet(image, POMS(position + anchor, 0, momentum * bullet_speed, 0),
                    group, world=world)
    bullet.mutators.add(MomentumMutator(bullet))


def danmaku_demo_00(position, sprite_factory, aim=0):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-cyan'](),
                             pe.bullets.CORES['tiny-lightblue']())

    bullets = 21
    ring = pe.Ring(0, bullets, width=60, aim=90)
    heartbeat = pe.Heartbeat(1, '#..........#........................')
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, aim=1)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_01(position, sprite_factory, aim=0, turn=0):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-yellow'](),
                             pe.bullets.CORES['tiny-lightblue']())

    bullets = 3
    ring = pe.Ring(0, bullets, width=60, aim=90)
    heartbeat = pe.Heartbeat(1, '############........................')
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, aim=1, turn=turn)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_02(position, sprite_factory, aim=0, turn=0):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-magenta'](),
                             pe.bullets.CORES['tiny-lightblue']())

    bullets = 4
    ring = pe.Ring(0, bullets, aim=90, width=40)
    heartbeat = pe.Heartbeat(1, '..............####################..')
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, aim=1, turn=turn)

    return pe.Factory(bullet_source, sprite_factory_)


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    world = SCREEN.scale_by(1.2)
    group = pygame.sprite.Group()

    patterns = [
        danmaku_demo_00(vec2(SCREEN.midtop), partial(sprite_factory, world=world, group=group)),
        danmaku_demo_01(vec2(SCREEN.midtop), partial(sprite_factory, world=world, group=group)),
        danmaku_demo_02(vec2(SCREEN.midtop), partial(sprite_factory, world=world, group=group)),
    ]

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, DT_MAX)

        for e in pygame.event.get():
            match e.type:
                case pygame.QUIT:
                    running = False

                case pygame.KEYDOWN:
                    match e.key:
                        case pygame.K_ESCAPE:
                            running = False

        screen.fill('black')

        for p in patterns:
            p.update(dt)

        group.update(dt)
        group.draw(screen)
        pygame.draw.circle(screen, 'grey20', SCREEN.center, 10, width=1)

        pygame.display.flip()

        runtime = pygame.time.get_ticks() / 1000
        fps = clock.get_fps()
        sprites = len(group)
        pygame.display.set_caption(f'{TITLE} - {runtime=:.2f}  {fps=:.2f}  {sprites=}')

    pygame.quit()


if __name__ == "__main__":
    main()

