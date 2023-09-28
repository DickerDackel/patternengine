import glm
import pygame
import patternengine as pe

from functools import partial
from pgcooldown import Cooldown, LerpThing
from glm import vec2

from patternengine.bullet import Bullet
from patternengine.poms import POMS, MomentumMutator, TurnMutator, AlignWithMomentumMutator

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
# SCREEN = pygame.Rect(0, 0, 640, 480)
FPS = 60
DT_MAX = 3 / FPS

BULLET_SPEED = 150
TURN = 37


def sprite_factory(position, momentum, anchor, bullet_speed, image, world,
                   group, turn=0, cls=Bullet, **kwargs):
    bullet = Bullet(image, POMS(position + anchor, 0, momentum * bullet_speed, turn),
                    group, world=world)
    bullet.mutator.add(MomentumMutator(bullet))
    if turn:
        bullet.mutator.add(TurnMutator(bullet))

    bullet.mutator.add(AlignWithMomentumMutator(bullet))


def danmaku_demo_00(position, sprite_factory, aim=0, turn=0):
    image = pe.bullets.merge(pe.bullets.DIAMONDS['small-ring-danmaku-magenta'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets)
    heartbeat = pe.Heartbeat(1, '########')
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, aim=1, turn=turn)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_01(position, sprite_factory, aim=0, turn=0):
    image = pe.bullets.merge(pe.bullets.ARROWHEADS['small-ring-danmaku-yellow'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets)
    heartbeat = pe.Heartbeat(1, '########')
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

    LTCD = 0.66
    TURN = 30
    patterns = [
        danmaku_demo_00(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=TURN,  aim=LerpThing(   0,   90, LTCD, repeat=2)),
        danmaku_demo_00(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=-TURN, aim=LerpThing( 180,   90, LTCD, repeat=2)),
        danmaku_demo_00(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=-TURN, aim=LerpThing(   0,  -90, LTCD, repeat=2)),
        danmaku_demo_00(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=TURN,  aim=LerpThing(-180,  -90, LTCD, repeat=2)),
        danmaku_demo_01(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=-TURN, aim=LerpThing( 90,     0, LTCD, repeat=2)),
        danmaku_demo_01(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=TURN,  aim=LerpThing(  90,  180, LTCD, repeat=2)),
        danmaku_demo_01(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=TURN,  aim=LerpThing( -90,    0, LTCD, repeat=2)),
        danmaku_demo_01(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), turn=-TURN, aim=LerpThing( -90, -180, LTCD, repeat=2)),
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
