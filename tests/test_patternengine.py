import glm
import pytest  # noqa: F401
import patternengine as pe

from time import sleep
from pytest import approx


def test_ring_circle():
    r = pe.Ring(100, 4)
    v = next(r)[0]
    assert approx(v.x, abs=0.001) == 100 and approx(v.y, abs=0.001) == 0
    v = next(r)[0]
    assert approx(v.x, abs=0.001) == 0 and approx(v.y, abs=0.001) == 100
    v = next(r)[0]
    assert approx(v.x, abs=0.001) == -100 and approx(v.y, abs=0.001) == 0
    v = next(r)[0]
    assert approx(v.x, abs=0.001) == 0 and approx(v.y, abs=0.001) == -100
    v = next(r)[0]
    assert approx(v.x, abs=0.001) == 100 and approx(v.y, abs=0.001) == 0


def test_ring_arc():
    r = pe.Ring(100, 3, width=90)
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == -45
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == 0
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == 45


def test_ring_arc_aim():
    r = pe.Ring(100, 3, width=90, aim=45)
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == 0
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == 45
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == 90


def test_ring_heartbeat():
    r = pe.Ring(100, 3, aim=90, width=180, heartbeat='#.#')
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == 0
    assert next(r) is None
    assert approx(glm.degrees(glm.atan2(*next(r)[0].yx)), abs=0.001) == -180


def test_heartbeat():
    h = pe.Heartbeat(1, '#.#.#.')
    assert next(h)
    assert not next(h)
    sleep(0.4)
    assert not next(h)
    sleep(0.1)
    assert next(h)


def test_bullet_source():
    b = pe.BulletSource(bullets=4,
                        ring=pe.Ring(100, 4),
                        heartbeat=pe.Heartbeat(1, '####'))
    lst = next(b)
    assert len(lst) == 4
    sleep(0.125)
    lst = next(b)
    assert len(lst) == 0
    sleep(0.125)
    lst = next(b)
    assert len(lst) == 4


if __name__ == "__main__":
    test_ring_circle()
    test_ring_arc()
    test_ring_arc_aim()
    test_ring_heartbeat()
    test_heartbeat()
    test_bullet_source()
