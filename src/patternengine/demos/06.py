import glm
import pygame
import patternengine as pe

from functools import partial
from pgcooldown import Cooldown, LerpThing
from glm import vec2

from patternengine.bullet import Bullet
from patternengine.poms import (POMS, Mutator, AccelerationMutator,
                                AlignWithAccelerationMutator,
                                AlignWithMomentumMutator, MomentumMutator)

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
# SCREEN = pygame.Rect(0, 0, 640, 480)
FPS = 60
DT_MAX = 3 / FPS

BULLET_SPEED = 250
TURN = 37


def sprite_factory(position, momentum, *, anchor=None, bullet_speed, image,
                   world, group, acceleration=0, max_speed=0, mutators=None,
                   factory_momentum=None, **kwargs):

    if anchor is None: anchor = vec2()
    if factory_momentum is None: factory_momentum = vec2()

    bullet = Bullet(image,
                    POMS(position + anchor, 0,
                         momentum * bullet_speed + factory_momentum, 0,
                         max_speed=max_speed),
                    group,
                    world=world)
    bullet.mutators.add(MomentumMutator(bullet))

    if acceleration:
        v = glm.normalize(momentum) * acceleration
        bullet.mutators.add(AccelerationMutator(bullet, v))
        bullet.mutators.add(AlignWithAccelerationMutator(bullet))
    else:
        bullet.mutators.add(AlignWithMomentumMutator(bullet))

    if mutators:
        bullet.mutators.add([m(bullet) for m in mutators])

    return bullet


def danmaku_demo_00(position, sprite_factory):
    image = pe.bullets.merge(pe.bullets.CIRCLES['tiny-ring-danmaku-yellow'](),
                             pe.bullets.CORES['tiny-lightblue']())

    bullets = 24
    ring = pe.Ring(0, bullets)
    heartbeat = pe.Heartbeat(0.5, '#')
    bullet_source = pe.BulletSource(bullets, ring, heartbeat)
    stack = pe.Stack(bullet_source, height=3, gain=1.05)

    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=-BULLET_SPEED,
                              image=image)

    return pe.Factory(stack, sprite_factory_)


def danmaku_demo_01(position, sprite_factory):
    class MyTurnMutator(Mutator):
        """Make the bullet turn a bit once the direction of momentum changes."""
        def __init__(self, parent, angle, max_speed, poms='poms'):
            super().__init__(parent)
            self.angle = glm.radians(angle)
            self.max_speed = max_speed
            self.poms = poms

        def __call__(self, dt):
            poms = getattr(self.parent, self.poms)
            a_mutator = self.parent.mutators[AccelerationMutator]

            m_direction = glm.normalize(poms.momentum)
            a_direction = glm.normalize(a_mutator.acceleration)

            if glm.dot(m_direction, a_direction) > 0:
                poms.momentum = glm.rotate(poms.momentum, self.angle)
                a_mutator.acceleration = glm.rotate(a_mutator.acceleration, self.angle)

                del self.parent.mutators[type(self)]
                del self.parent.mutators[AlignWithAccelerationMutator]
                self.parent.mutators.add(AlignWithMomentumMutator(self.parent))
                poms.max_speed = self.max_speed

    image = pe.bullets.merge(pe.bullets.ARROWHEADS['small-ring-danmaku-green'](),
                             pe.bullets.CORES['small-lightblue']())

    bullets = 8
    ring = pe.Ring(0, bullets)
    heartbeat = pe.Heartbeat(2.5, '#')
    aim = LerpThing(0, 360, 10, repeat=1)
    bullet_source = pe.BulletSource(bullets, ring, heartbeat, aim)
    stack = pe.Stack(bullet_source, height=5, gain=1.1)

    my_mutator = partial(MyTurnMutator, angle=25, max_speed=150)
    sprite_factory_ = partial(sprite_factory, anchor=position,
                              bullet_speed=-200, image=image,
                              acceleration=150,
                              mutators=[my_mutator])

    return pe.Factory(stack, sprite_factory_)


def danmaku_demo_02(position, sprite_factory, target):
    class AimFactoryMutator(Mutator):
        def __init__(self, parent, target):
            super().__init__(parent)
            self.target = target

        def __call__(self, dt):
            p0 = self.parent.poms.position
            p1 = vec2(self.target.rect.center)
            v = p1 - p0
            angle = -glm.degrees(glm.atan2(*v) + glm.half_pi())
            self.parent.poms.orientation = angle

    class AccelerateTowardsTargetMutator(Mutator):
        def __init__(self, parent, target, force, duration):
            super().__init__(parent)
            self.target = target
            self.force = force
            self.duration = Cooldown(duration)
            self.v = None

        def __call__(self, dt):
            if self.duration.cold():
                del self.parent.mutators[AccelerateTowardsTargetMutator]
                return

            p0 = self.parent.poms.position
            p1 = vec2(self.target.rect.center)
            v = glm.normalize(p1 - p0) * self.force

            self.parent.poms.momentum += v * dt

    image = pe.bullets.merge(pe.bullets.OVALS['tiny-ring-magenta'](),
                             pe.bullets.CORES['tiny-lightblue']())

    bullets = 8
    ring = pe.Ring(0, bullets, aim=-30, width=60, randomize=True)
    heartbeat = pe.Heartbeat(3, '................########')
    bullet_source = pe.BulletSource(bullets, ring, heartbeat)

    poms = POMS(position)

    thrust = partial(AccelerateTowardsTargetMutator,
                     target=target, force=350, duration=2.5)
    sprite_factory_ = partial(sprite_factory, bullet_speed=350, image=image,
                              mutators=[thrust])

    factory = pe.Factory(bullet_source, sprite_factory_, poms=poms)
    factory.mutators.add(AimFactoryMutator(factory, target))
    return factory


class Target(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((32, 32))
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, 'red', self.rect.center, self.rect.width // 2, width=2)

        self.xpos = LerpThing(250, SCREEN.width - 250, 5, repeat=2)

    def update(self, dt):
        self.rect.center = (self.xpos(), SCREEN.height / 4 * 3)


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    world = SCREEN.scale_by(1.2)
    group = pygame.sprite.Group()
    group.add(target := Target())

    patterns = [
        danmaku_demo_00(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group)),
        danmaku_demo_01(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group)),
        danmaku_demo_02(vec2(SCREEN.center), partial(sprite_factory, world=world, group=group), target=target),
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
