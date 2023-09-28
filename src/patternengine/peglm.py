from glm import vec2, normalize, length


def scale_to(v: vec2, l: float):
    return normalize(v) * l


def scale_by(v: vec2, f: float):
    return normalize(v) * length(v) * f


def clamp(v: vec2, l: float):
    return v if length(v) <= l else normalize(v) * l
