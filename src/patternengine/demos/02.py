import glm
import pygame
import patternengine as pe

from functools import partial
from pgcooldown import Cooldown, LerpThing
from glm import vec2

from patternengine.bullet import Bullet
from patternengine.poms import POMS, Mutator, MomentumMutator, TurnMutator, AlignWithMomentumMutator

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
SCREEN = pygame.Rect(0, 0, 640, 480)
FPS = 60
DT_MAX = 3 / FPS

BULLET_SPEED = 150
TURN = 30


class ZigZagMutator(Mutator):
    def __init__(self, parent, zigzag, cooldown, poms='poms'):
        super().__init__(parent)
        self.cd = Cooldown(cooldown)
        self.initial = True
        self.angle = glm.radians(zigzag)
        self.poms = poms

    def __call__(self, dt):
        poms = getattr(self.parent, self.poms)
        if self.cd.cold():
            if self.initial:
                self.initial = False
                poms.momentum = glm.rotate(poms.momentum, self.angle / 2)
            else:
                poms.momentum = glm.rotate(poms.momentum, self.angle)

            self.cd.reset()
            self.angle = -self.angle


def sprite_factory(position, momentum, anchor, bullet_speed, image, world,
                   group, turn=0, zigzag=None, **kwargs):
    bullet = Bullet(image,
                    POMS(position + anchor, 0, momentum * bullet_speed, turn),
                    group, world=world)
    bullet.mutators.add(MomentumMutator(bullet))

    if turn:
        bullet.mutators.add(TurnMutator(bullet))
        bullet.mutators.add(AlignWithMomentumMutator(bullet))

    if zigzag:
        bullet.mutators.add(ZigZagMutator(bullet, zigzag, 1 / 3))

    return bullet


def danmaku_demo_00(position, sprite_factory):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-danmaku-magenta'](),
                             pe.bullets.CORES['tiny-danmaku-magenta']())

    bullets = 24
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(1, '#...#...#...#...')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED, turn=TURN,
                              image=image)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_01(position, sprite_factory):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-danmaku-green'](),
                             pe.bullets.CORES['tiny-danmaku-green']())

    bullets = 24
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(1, '..#...#...#...#.')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              turn=-TURN, image=image)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_02(position, sprite_factory):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-danmaku-yellow'](),
                             pe.bullets.CORES['tiny-danmaku-yellow']())

    bullets = 6
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(1.5, '################                ')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image,
                              zigzag=45)

    return pe.Factory(bullet_source, sprite_factory_)


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    world = SCREEN.scale_by(1.2)
    groups = {
        'top': pygame.sprite.Group(),
        'middle': pygame.sprite.Group(),
        'bottom': pygame.sprite.Group(),
    }
    anchor = vec2(SCREEN.center)

    patterns = [
        danmaku_demo_00(anchor, partial(sprite_factory, world=world, group=groups['bottom'])),
        danmaku_demo_01(anchor, partial(sprite_factory, world=world, group=groups['middle'])),
        danmaku_demo_02(anchor, partial(sprite_factory, world=world, group=groups['top'])),
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

        groups['bottom'].update(dt)
        groups['middle'].update(dt)
        groups['top'].update(dt)
        groups['bottom'].draw(screen)
        groups['middle'].draw(screen)
        groups['top'].draw(screen)
        pygame.draw.circle(screen, 'grey20', SCREEN.center, 10, width=1)

        pygame.display.flip()
        pygame.display.set_caption(f'{TITLE} - time={pygame.time.get_ticks()/1000:.2f}  fps={clock.get_fps():.2f}')

    pygame.quit()


if __name__ == "__main__":
    main()
