# Use Arcade for the presentation layer

Replace Tkinter and CustomTkinter with Arcade 3.x after the headless Game Engine has been extracted. The Snake app is game-first, and Arcade provides game rendering, a game loop, GUI widgets, and switchable views in one framework without the desktop-application complexity of Qt.

## Considered Options

- Arcade 3.x
- pygame-ce with pygame_gui
- PySide6

Arcade was selected because its View model fits the app's Menu, Settings, Game, Replay, and Records screens while providing more structure than pygame-ce and remaining more game-focused than PySide6.

## Consequences

- The app will use one Arcade window and switch between App Views.
- The Game Engine will remain independent of Arcade.
- The first migrated version will preserve all current features and use a fixed-size window.
- The migration will not add human controls, animation, sound, or other gameplay features.
- The presentation layer will support macOS, Windows, and Linux.
