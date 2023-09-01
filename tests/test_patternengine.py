import pytest
import patternengine as pe

from time import sleep

from pygame import Vector2
from pytest import approx


def test_ring_circle():
    r = pe.Ring(100, 4)
    assert next(r)[0] == Vector2(100, 0)
    assert next(r)[0] == Vector2(0, 100)
    assert next(r)[0] == Vector2(-100, 0)
    assert next(r)[0] == Vector2(0, -100)
    assert next(r)[0] == Vector2(100, 0)


def test_ring_arc():
    r = pe.Ring(100, 3, width=90)
    assert next(r)[0].as_polar()[1] == approx(-45)
    assert next(r)[0].as_polar()[1] == approx(0)
    assert next(r)[0].as_polar()[1] == approx(45)


def test_ring_arc_aim():
    r = pe.Ring(100, 3, width=90, aim=45)
    assert next(r)[0].as_polar()[1] == approx(0)
    assert next(r)[0].as_polar()[1] == approx(45)
    assert next(r)[0].as_polar()[1] == approx(90)


def test_ring_heartbeat():
    r = pe.Ring(100, 3, aim=90, width=180, heartbeat='#.#')
    assert next(r)[0].as_polar()[1] == approx(0)
    assert next(r) is None
    assert next(r)[0].as_polar()[1] == approx(-180)


def test_ring_update_step():
    r = pe.Ring(100, 4)
    assert r.steps == 4

    r.steps = 8
    assert r.steps == 8
    assert next(r)[0].as_polar()[1] == approx(0)
    assert next(r)[0].as_polar()[1] == approx(45)


def test_ring_update_heartbeat():
    with pytest.raises(ValueError) as e:
        r = pe.Ring(100, 1, heartbeat='lorem ipsum')  # noqa: F841
    assert e.type is ValueError


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
    test_ring_update_step()
    test_ring_update_heartbeat()
    test_heartbeat()
    test_bullet_source()
