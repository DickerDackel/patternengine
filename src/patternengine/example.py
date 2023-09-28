import pygame
import patternengine as pe

from pgcooldown import Cooldown
from pygame import Vector2


TITLE = 'Minimal patternengine example'
SCREEN = pygame.Rect(0, 0, 1024, 768)
FPS = 60
DT_MAX = 3 / FPS


class Bullet(pygame.sprite.Sprite):
    """Just a sprite that moves on a straight line."""
    def __init__(self, *groups, position, momentum, lifetime):
        super().__init__(*groups)

        self.position = position
        self.momentum = momentum
        self.lifetime = lifetime if isinstance(lifetime, Cooldown) else Cooldown(lifetime)

        self.image = pygame.Surface((16, 16))
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, 'white', self.rect.center, self.rect.centerx)

    def update(self, dt):
        if self.lifetime.cold():
            self.kill
            return

        self.position += self.momentum * dt
        self.rect.center = self.position


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    group = pygame.sprite.Group()

    ########################################################################
    # Relevant part here
    #
    # A "ring" of 180 degrees aiming towards the top devided int 30 parts,
    #     with a pattern of allowed and empty positions.
    # A heartbeat over 1 seconds with a comple
    # A BulletSource fetching 18 bullets at every heartbeat
    #

    ring = pe.Ring(100, 30, aim=-90, width=180,
                   heartbeat='##....###....##', jitter=3)
    heartbeat = pe.Heartbeat(1, '###.#.#.')
    emitter = pe.BulletSource(30, ring, heartbeat)

    #
    ########################################################################

    anchor = Vector2(SCREEN.centerx, SCREEN.height / 3 * 2)
    bullet_speed = 100

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, DT_MAX)

        for e in pygame.event.get():
            match e.type:
                case pygame.QUIT:
                    running = False

                case pygame.KEYDOWN if e.key == pygame.K_ESCAPE:
                    running = False

        screen.fill('black')

        ####################################################################
        # Relevant part here
        #
        for bullet in next(emitter):
            Bullet(group,
                   position=bullet[0] + anchor,
                   momentum=bullet[1] * bullet_speed,
                   lifetime=10)
        #
        ####################################################################

        group.update(dt)
        group.draw(screen)

        pygame.display.flip()
        pygame.display.set_caption(f'{TITLE} - time={pygame.time.get_ticks()/1000:.2f}  fps={clock.get_fps():.2f}')

    pygame.quit()


if __name__ == "__main__":
    main()
