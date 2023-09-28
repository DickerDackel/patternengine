import pygame
import patternengine as pe

from functools import partial
from pgcooldown import Cooldown, LerpThing
from glm import vec2

from patternengine.bullet import Bullet
from patternengine.poms import POMS, MomentumMutator, AimTargetMutator, SpinMutator

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
# SCREEN = pygame.Rect(0, 0, 640, 480)
FPS = 60
DT_MAX = 3 / FPS

BULLET_SPEED = 150
TURN = 37


def sprite_factory(position, momentum, anchor, bullet_speed, image, world,
                   group, target=None, spin=0, **kwargs):
    bullet = Bullet(image, POMS(position + anchor, 0, momentum * bullet_speed, spin),
                    group, world=world)
    bullet.mutator.add(MomentumMutator(bullet))

    if target:
        bullet.mutator.add(AimTargetMutator(bullet, target=target))

    if spin:
        bullet.mutator.add(SpinMutator(bullet))


def danmaku_demo_00(position, sprite_factory):
    image = pe.bullets.merge(pe.bullets.CIRCLES['small-ring-brown'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(2, '#.#.#.#.')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_01(position, sprite_factory):
    image = pe.bullets.merge(pe.bullets.SQUARES['small-ring-cyan'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(2, '#.#.#.#.')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, spin=360)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_02(position, sprite_factory, *args, **kwargs):
    image = pe.bullets.merge(pe.bullets.DIAMONDS['small-ring-danmaku-magenta'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(2, '#.#.#.#.')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, **kwargs)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_03(position, sprite_factory, **kwargs):
    image = pe.bullets.merge(pe.bullets.OVALS['small-ring-danmaku-yellow'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(2, '#.#.#.#.')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, **kwargs)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_04(position, sprite_factory, **kwargs):
    image = pe.bullets.merge(pe.bullets.TRIANGLES['small-ring-danmaku-green'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(2, '#.#.#.#.')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image, **kwargs)

    return pe.Factory(bullet_source, sprite_factory_)


def danmaku_demo_05(position, sprite_factory):
    image = pe.bullets.merge(pe.bullets.ARROWHEADS['small-ring-magenta'](),
                             pe.bullets.CORES['small-white']())

    bullets = 1
    ring = pe.Ring(0, bullets, aim=0)
    heartbeat = pe.Heartbeat(2, '#.#.#.#.')
    aim = 0
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=BULLET_SPEED,
                              image=image)

    return pe.Factory(bullet_source, sprite_factory_)


class Mouse(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.poms = POMS(vec2(), 0, vec2(), 0)
        self.image = pygame.Surface((16, 16))
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, 'red', self.rect.center, self.rect.width // 2, width=2)

    def update(self, dt):
        self.poms.position = vec2(pygame.mouse.get_pos())
        self.rect.center = self.poms.position


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    world = SCREEN.scale_by(1.2)
    group = pygame.sprite.Group()
    mouse = Mouse(group)

    patterns = [
        danmaku_demo_00(vec2(50, SCREEN.centery - 80), partial(sprite_factory, world=world, group=group)),
        danmaku_demo_01(vec2(50, SCREEN.centery - 48), partial(sprite_factory, world=world, group=group)),
        danmaku_demo_02(vec2(50, SCREEN.centery - 16), partial(sprite_factory, world=world, group=group, target=mouse, aim=1)),
        danmaku_demo_03(vec2(50, SCREEN.centery + 16), partial(sprite_factory, world=world, group=group, target=mouse, aim=1)),
        danmaku_demo_04(vec2(50, SCREEN.centery + 48), partial(sprite_factory, world=world, group=group, target=mouse, aim=1)),
        danmaku_demo_05(vec2(50, SCREEN.centery + 80), partial(sprite_factory, world=world, group=group, target=mouse, aim=1)),
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
