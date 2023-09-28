"""Bullet image factories and preconfigured bullets.

patternengine comes with a set of preconfigured bullet factories to ease
experimenting with the library.

To create your own sizes and colors, see the documentation of
`bullet_image_factory` below.

The preconfigured factories can be found in the `BULLET_FACTORIES` dict under
their specific name in the following schema:

    SIZE[-ring]-COLOR

with the available sizes

    tiny         radius=4
    small        radius=6
    medium       radius=12
    large        radius=16
    larger       radius=24
    tiny-ring    radius=4
    small-ring   radius=6
    medium-ring  radius=12
    large-ring   radius=16
    larger-ring  radius=24

and colors

    pink, cyan, yellow, lightblue, green, red

So, if you need e.g. a pink medium sized sprite with a ring, you can get this
it like this:

    patternengine.bullets.BULLETS['medium-ring-pink']

"""

import pygame

from functools import partial
from rpeasings import *  # noqa: F403

STROKE_SCALE = 1 / 8

stroke_width = lambda size: min(int(size * STROKE_SCALE), 3)


def merge(shape, core):
    cs_rect = shape.get_rect()
    co_rect = core.get_rect(center=cs_rect.center)

    image = shape.copy()
    image.blit(core, co_rect)
    return image


def core_factory(size, color, gradient=in_quad, debug=False, *kwargs):  # noqa: F405
    r0 = int((3 / 4) * size) // 2

    image = pygame.Surface((size, size))
    image.set_colorkey('black')
    rect = image.get_rect()

    c0 = pygame.Color('white')
    c1 = pygame.Color(color)

    for r in range(r0, 1, -1):
        t = gradient(r / r0)  # noqa: F405
        color = c0.lerp(c1, t)
        pygame.draw.circle(image, color, rect.center, r)

    if debug: pygame.draw.line(image, 'red', rect.center, rect.midright, width=1)
    return image


def circle_factory(size, color, debug=False):  # noqa: F405
    r = size // 2
    image = pygame.Surface((size, size))
    image.set_colorkey('black')
    rect = image.get_rect()

    stroke = max(1, stroke_width(size))

    pygame.draw.circle(image, color, rect.center, r, width=stroke)

    if debug: pygame.draw.line(image, 'red', rect.center, rect.midright, width=1)
    return image


def square_factory(size, color, debug=False):
    image = pygame.Surface((size, size))
    image.set_colorkey('black')
    rect = image.get_rect()

    stroke = max(1, stroke_width(size))

    pygame.draw.rect(image, color, rect, width=stroke)

    if debug: pygame.draw.line(image, 'red', rect.center, rect.midright, width=1)
    return image


def diamond_factory(size, color, debug=False):
    stroke = max(1, stroke_width(size))

    image = pygame.Surface((2 * size, size))
    image.set_colorkey('black')
    rect = image.get_rect()
    rect.width -= 1
    rect.height -= 1
    pygame.draw.rect(image, 'black', rect, 1)

    points = [rect.midtop, rect.midright, rect.midbottom, rect.midleft]
    pygame.draw.polygon(image, color, points, width=stroke)

    if debug: pygame.draw.line(image, 'red', rect.center, rect.midright, width=1)
    return image


def triangle_factory(size, color, debug=False):
    size *= 1.75
    height = size * 0.75 ** 0.5
    shift = size / 2 - (height / 3 - 1)
    oversize = 2 * 2 * height / 3

    tri = pygame.Surface((size, size))
    tri.set_colorkey('black')
    r_tri = tri.get_rect()
    r_tri.width -= 1
    r_tri.height -= 1

    stroke = max(1, stroke_width(size))

    points = [(0, 0), (0, r_tri.width), (height, r_tri.centery), (0, 0)]
    pygame.draw.polygon(tri, color, points, width=stroke)

    image = pygame.Surface((oversize, oversize))
    image.set_colorkey('black')
    rect = image.get_rect()

    r_tri.centerx = rect.centerx + shift - 2
    r_tri.centery = rect.centery - 1

    image.blit(tri, r_tri)

    if debug: pygame.draw.line(image, 'red', rect.center, rect.midright, width=1)
    return image


def oval_factory(size, color, debug=False):
    image = pygame.Surface((2 * size, size))
    image.set_colorkey('black')
    rect = image.get_rect()

    stroke = max(1, stroke_width(size))
    pygame.draw.ellipse(image, color, rect, width=stroke)

    if debug: pygame.draw.line(image, 'red', rect.center, rect.midright, width=1)
    return image


def arrowhead_factory(size, color, debug=False):
    image = pygame.Surface((size, size))
    image.set_colorkey('black')
    rect = image.get_rect()

    e_rect = pygame.Rect(0, 0, size * 2, size)
    e_rect.centerx = 0

    stroke = max(1, stroke_width(size))
    pygame.draw.ellipse(image, color, e_rect, width=stroke)

    if debug: pygame.draw.line(image, 'red', rect.center, rect.midright, width=1)
    return image


def bullet_image_factory(kind, *args, **kwargs):
    return {
        'core': core_factory,
        'circle': circle_factory,
        'square': square_factory,
        'diamond': diamond_factory,
        'triangle': triangle_factory,
        'oval': oval_factory,
        'arrowhead': arrowhead_factory,
    }[kind](*args, **kwargs)


BULLET_COLORS = {
    'white': 'white',
    'red': 'red',
    'green': 'green',
    'blue': 'blue',
    'cyan': 'cyan',
    'magenta': 'magenta',
    'yellow': 'yellow',
    'pink': 'hotpink',
    'orange': 'yellow',
    'brown': 'brown',
    'lightblue': 'lightblue',
    'danmaku-magenta': '#660066',
    'danmaku-yellow': '#ffff66',
    'danmaku-blue': '#0066ff',
    'danmaku-green': '#226655',
}

CORE_SIZES = {
    'tiny': 8,
    'small': 12,
    'medium': 20,
    'large': 24,
    'larger': 40,
    'extralarge': 56,
}

RING_SIZES = {
    'tiny-ring': 12,
    'small-ring': 16,
    'medium-ring': 24,
    'large-ring': 32,
    'larger-ring': 48,
    'extralarge-ring': 64,
}

CORES = {
    f'{s}-{c}': partial(core_factory,
                        size=CORE_SIZES[s],
                        color=BULLET_COLORS[c])
    for s in CORE_SIZES
    for c in BULLET_COLORS
}

CIRCLES = {
    f'{s}-{c}': partial(circle_factory,
                        size=RING_SIZES[s],
                        color=BULLET_COLORS[c])
    for s in RING_SIZES
    for c in BULLET_COLORS
}

SQUARES = {
    f'{s}-{c}': partial(square_factory,
                        size=RING_SIZES[s],
                        color=BULLET_COLORS[c])
    for s in RING_SIZES
    for c in BULLET_COLORS
}

DIAMONDS = {
    f'{s}-{c}': partial(diamond_factory,
                        size=RING_SIZES[s],
                        color=BULLET_COLORS[c])
    for s in RING_SIZES
    for c in BULLET_COLORS
}

TRIANGLES = {
    f'{s}-{c}': partial(triangle_factory,
                        size=RING_SIZES[s],
                        color=BULLET_COLORS[c])
    for s in RING_SIZES
    for c in BULLET_COLORS
}

OVALS = {
    f'{s}-{c}': partial(oval_factory,
                        size=RING_SIZES[s],
                        color=BULLET_COLORS[c])
    for s in RING_SIZES
    for c in BULLET_COLORS
}

ARROWHEADS = {
    f'{s}-{c}': partial(arrowhead_factory,
                        size=RING_SIZES[s],
                        color=BULLET_COLORS[c])
    for s in RING_SIZES
    for c in BULLET_COLORS
}
