"""
The graphical user interface for Ritual, built with pygame-ce.

PygameUI (pygame_ui.py) has the same methods as TerminalUI, so Game does not
need to change: show_event, choose_move, choose_card and choose_mulligan.
The other modules each have one job:
   assets.py   - finds and loads the images
   layout.py   - where everything is on the screen
   renderer.py - draws cards, portraits and heroes
   effects.py  - short animations (flying numbers, attack lines, banners)
"""
