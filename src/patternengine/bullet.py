import pygame

from types import SimpleNamespace
from patternengine.poms import MutatorStack

__all__ = ['Bullet']


class RSAImage:
    cache = {}
    stats = SimpleNamespace(hits=0, misses=0)
    images = set()

    def __init__(self, rotate_chunk=5, scale_chunk=1, alpha_chunk=5):
        self.r_chunk = lambda r: self.chunk(r, rotate_chunk)
        self.s_chunk = lambda s: round(s, scale_chunk)
        self.a_chunk = lambda a: self.chunk(a, alpha_chunk)
        self.tag = lambda i, r, s, a: f'{id(i)}-{r}-{s}-{a}'

    def clear(self):
        self.cache.empty()

    def __set__(self, inst, image):
        inst._rsai_base_image = image
        tag = self.tag(image, 0, 1, 255)
        self.cache[tag] = image

    def __get__(self, inst, cls):
        base_image = inst._rsai_base_image
        self.images.add(id(base_image))
        rotate = self.r_chunk(inst.poms.orientation) if hasattr(inst, 'poms') else 0
        scale = self.s_chunk(inst.scale) if hasattr(inst, 'scale') else 1
        alpha = self.a_chunk(inst.alpha) if hasattr(inst, 'alpha') else 255

        tag = self.tag(base_image, rotate, scale, alpha)
        if tag not in self.cache:
            self.stats.misses += 1
            self.cache[tag] = self.generate(base_image, rotate, scale, alpha)
        else:
            self.stats.hits += 1

        inst.rect = self.cache[tag].get_rect(center=inst.rect.center)
        return self.cache[tag]

    def chunk(self, val, chunksize):
        return ((val + chunksize // 2) // chunksize) * chunksize if chunksize else val

    def generate(self, base_image, rotate, scale, alpha):
        image = base_image
        if rotate:
            image = pygame.transform.rotate(image, rotate)

        if scale != 1:
            image = pygame.transform.smoothscale_by(image, scale)

        if alpha != 255:
            if image is base_image:
                image = base_image.copy()
            image.set_alpha(alpha)

        return image


class Bullet(pygame.sprite.Sprite):

    image = RSAImage()

    def __init__(self, image, poms, *groups, mutator=None, world=None):
        super().__init__(*groups)

        self.image = image
        self.poms = poms
        self.rect = image.get_rect(center=poms.position)

        self.mutator = MutatorStack(mutator) if mutator else MutatorStack()
        self.world = world

    def update(self, dt):
        for m in list(self.mutator.values()): m(dt)

        self.rect.center = self.poms.position

        if self.world and not self.world.collidepoint(self.poms.position):
            self.kill()
