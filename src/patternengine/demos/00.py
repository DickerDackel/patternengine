import pygame
import patternengine as pe

from itertools import cycle
from pgcooldown import Cooldown

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
FPS = 60
DT_MAX = 3 / FPS


def gen_bullet_set(bset, sizes, color):
    return [bset[f'{size}-{color}']() for size in sizes]


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode(SCREEN.size)
    clock = pygame.time.Clock()

    def generate_set(color):
        core_color = 'lightblue' if color == 'white' else color

        cores = gen_bullet_set(pe.bullets.CORES, pe.bullets.CORE_SIZES, core_color)
        circles = gen_bullet_set(pe.bullets.CIRCLES, pe.bullets.RING_SIZES, color)
        squares = gen_bullet_set(pe.bullets.SQUARES, pe.bullets.RING_SIZES, color)
        diamonds = gen_bullet_set(pe.bullets.DIAMONDS, pe.bullets.RING_SIZES, color)
        triangles = gen_bullet_set(pe.bullets.TRIANGLES, pe.bullets.RING_SIZES, color)
        ovals = gen_bullet_set(pe.bullets.OVALS, pe.bullets.RING_SIZES, color)
        arrowheads = gen_bullet_set(pe.bullets.ARROWHEADS, pe.bullets.RING_SIZES, color)

        core_circles = [pe.bullets.merge(shape, core) for shape, core in zip(circles, cores)]
        core_squares = [pe.bullets.merge(shape, core) for shape, core in zip(squares, cores)]
        core_diamonds = [pe.bullets.merge(shape, core) for shape, core in zip(diamonds, cores)]
        core_triangles = [pe.bullets.merge(shape, core) for shape, core in zip(triangles, cores)]
        core_ovals = [pe.bullets.merge(shape, core) for shape, core in zip(ovals, cores)]
        core_arrowheads = [pe.bullets.merge(shape, core) for shape, core in zip(arrowheads, cores)]

        return [cores, circles, squares, diamonds, triangles, ovals,
                arrowheads, core_circles, core_squares, core_diamonds,
                core_triangles, core_ovals, core_arrowheads]

    colors = cycle(pe.bullets.BULLET_COLORS)
    color = next(colors)

    images = generate_set(color)

    color_cooldown = Cooldown(2)
    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, DT_MAX)  # noqa: F841

        for e in pygame.event.get():
            match e.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN if e.key == pygame.K_ESCAPE:
                    raise SystemExit
        if color_cooldown.cold():
            color_cooldown.reset()
            color = next(colors)
            images = generate_set(color)

        screen.fill('black')

        xpos = [32 + i * 64 for i in range(len(images[0]))]
        xpos[-2] += 32
        xpos[-1] += 95

        for x, img in zip(xpos, images[0]):
            screen.blit(img, img.get_rect(center=(x, 50)))

        for y in range(6):
            for x, img in zip(xpos, images[y + 1]):
                screen.blit(img, img.get_rect(center=(x, 50 + y * 110)))

        w2 = SCREEN.width / 2
        for y in range(6):
            for x, img in zip(xpos, images[y + 1 + 6]):
                screen.blit(img, img.get_rect(center=(w2 + x, 50 + y * 110)))

        pygame.display.flip()
        pygame.display.set_caption(f'{TITLE} - time={pygame.time.get_ticks()/1000:.2f}  fps={clock.get_fps():.2f}')

    pygame.quit()


if __name__ == "__main__":
    main()
