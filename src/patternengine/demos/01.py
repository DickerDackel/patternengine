import pygame
import patternengine as pe

from functools import partial
from pgcooldown import LerpThing
from glm import vec2

from patternengine.bullet import Bullet
from patternengine.poms import POMS, MomentumMutator

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
SCREEN = pygame.Rect(0, 0, 640, 480)
FPS = 60
DT_MAX = 3 / FPS


def sprite_factory(position, momentum, anchor, bullet_speed, image, world,
                   group, **kwargs):
    bullet = Bullet(image,
                    POMS(position + anchor, 0, momentum * bullet_speed, 0),
                    group,
                    world=world)
    bullet.mutators.add(MomentumMutator(bullet))


def danmaku_demo_00(position, sprite_factory):
    bullet_speed = 80
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-danmaku-magenta'](),
                             pe.bullets.CORES['tiny-danmaku-magenta']())

    bullets = 24
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(1, '#')
    aim = LerpThing(0, 360, 7 / 3, repeat=1)
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    stack_height = 5
    stack_gain = 1.1
    stack = pe.Stack(bullet_source, stack_height, stack_gain)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=bullet_speed, image=image)

    return pe.Factory(stack, sprite_factory_)


def danmaku_demo_01(position, sprite_factory):
    bullet_speed = 180
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-danmaku-yellow'](),
                             pe.bullets.CORES['tiny-danmaku-yellow']())

    bullets = 4
    ring = pe.Ring(0, bullets, aim=0, heartbeat='#.#.')
    heartbeat = pe.Heartbeat(1 / 2.5, '#')
    aim = LerpThing(0, 360, 7 / 3, repeat=1)
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    stack_height = 5
    stack_gain = 1.1
    stack = pe.Stack(bullet_source, stack_height, stack_gain)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=bullet_speed, image=image)

    return pe.Factory(stack, sprite_factory_)


def danmaku_demo_02(position, sprite_factory):
    bullet_speed = 180
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-danmaku-blue'](),
                             pe.bullets.CORES['tiny-danmaku-blue']())

    bullets = 4
    ring = pe.Ring(60, bullets, aim=90, heartbeat='#.#.')
    heartbeat = pe.Heartbeat(1 / 2.5, '#')
    aim = LerpThing(0, 360, 7 / 3, repeat=1)
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    stack_height = 5
    stack_gain = 1.1
    stack = pe.Stack(bullet_source, stack_height, stack_gain)

    fan_arc = 360 / 24
    fan_steps = 3
    fan = pe.Fan(stack, fan_arc, fan_steps)

    sprite_factory_ = partial(sprite_factory, anchor=position, bullet_speed=bullet_speed, image=image)

    return pe.Factory(fan, sprite_factory_)


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    world = SCREEN.scale_by(1.2)
    group = pygame.sprite.Group()
    anchor = vec2(SCREEN.center)

    sprite_factory_ = partial(sprite_factory, world=world, group=group)

    patterns = [
        danmaku_demo_00(anchor, sprite_factory_),
        danmaku_demo_01(anchor, sprite_factory_),
        danmaku_demo_02(anchor, sprite_factory_),
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
        pygame.display.set_caption(f'{TITLE} - {runtime=:.2f}  fps={fps=:.2f}  {sprites=}')

    pygame.quit()


if __name__ == "__main__":
    main()
