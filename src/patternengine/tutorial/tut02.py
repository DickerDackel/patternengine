import glm
import pygame
import patternengine as pe

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
FPS = 60
DT_MAX = 3 / FPS

pygame.init()
pygame.display.set_caption(TITLE)
screen = pygame.display.set_mode(SCREEN.size)
clock = pygame.time.Clock()


group = pygame.sprite.Group()


def sprite_factory(position, momentum, *args, **kwargs):
    anchor = glm.vec2(SCREEN.center)
    bullet_speed = 150
    world = SCREEN.inflate(64, 64)

    image = pe.bullets.merge(pe.bullets.CIRCLES['medium-ring-danmaku-magenta'](),
                             pe.bullets.CORES['medium-danmaku-magenta']())
    position += anchor
    momentum *= bullet_speed

    poms = pe.POMS(position, 0, momentum, 0)
    bullet = pe.Bullet(image, poms, group)

    bullet.mutators.add(pe.MomentumMutator(bullet))
    bullet.mutators.add(pe.WorldMutator(bullet, world))

    return bullet


ring = pe.Ring(radius=0, steps=1)
heartbeat = pe.Heartbeat(duration=1, pattern='#')
bullet_source = pe.BulletSource(bullets=1, ring=ring, heartbeat=heartbeat)
factory = pe.Factory(bullet_source, sprite_factory)

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
