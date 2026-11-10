# v0.0.9

Lots of structural changes, we're in double-zero versions still.
This package has added sphinx docs.
The existing sprite and dynamics objects that are not directly tied to the
patternengine itself will move into different helper packages to have this
library completely backend independent.

In the near future, the best setup for patternengine will be

- pygame-ce
- tinyecs
- tinyecs-compsys-patternengine

# v0.0.6
- Tutorial
- More mutators, __all__
- Orientation wasn't inherited from the Factory
- Refactor Bullet attribute mutator to mutators
- Import POMS and mutators into patternengine namespace

# v0.0.4
- Big redesign - cleanups pending
- Added 6 demos to implement patterns from the ph3 tutorial website
- Some docs added for Stack, Fan, Factory
- rpeasings was missing in requirements
- Ported pygame.Vector2 to glm.vec2, also tests cleaned up
- Debugging removed, better core position in arrowhead

# v0.0.3
- Ring now has a heartbeat; jitter
- Added testing

# v0.0.2

- First published version
