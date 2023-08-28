import pygame

from enum import Enum
from types import SimpleNamespace

from pygamehelpers.framework import App

from patternengine.config import TITLE, SCREEN, FPS, States
from patternengine.title import Title
from patternengine.demo import Demo


def main():
    app = App(TITLE, SCREEN, FPS)

    persist = SimpleNamespace(
        font=pygame.Font(None),
    )

    states = {
        States.TITLE: Title(app, persist),
        States.DEMO: Demo(app, persist),
    }

    app.run(States.TITLE, states)


if __name__ == '__main__':
    main()
