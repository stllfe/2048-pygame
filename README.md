# 2048 Game
2048 written in Python using [pygame](https://github.com/pygame/pygame) library. The original game is created by [Gabriele Cirulli](https://github.com/gabrielecirulli/2048).

## About this project
This is a study project I was given at my uni. Even though we were asked to come up with any version of this game (e. g. terminal, web-based), I decided to play it hard and went all Python in 🤟

In fact, I got some **goals in mind** while designing this game in Python.
### Architecture
- [x] **UI and logic decoupled**: I want to be able to write UI-related code without touching anything else. That's why I came up with somewhat MVC-like concept.
- [x] **Event-based:** I went with Mediator pattern to decouple classes even better. It actually emerged as a solution for having different user input-controllers like keyboard, mouse, gesture, joystick (???). However, it turned out to be a powerful concept that both complements and tightens the whole project together.
- [x] **Framework agnostic**: The main source code is almost dependency free. My idea was to avoid writing code for some target framework or library, but instead to build up simple and concise high-level abstractions. The pygame library used here was more of a proof of concept that these building blocks are enough for further development.

### Codestyle
- [ ] **Redable and well documented**: I really admire the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html). I'd like to apply it here as well.


### Features
- [ ] Fancy animations
- [ ] Dynamic tiles' colors switching
- [X] User configuration via config-file
- [X] Progress saving and storage system
- [X] Custom board size (both vertical and horizontal)
- [ ] Custom window resolution and adaptive graphics scaling
- [ ] Color themes and dynamic theme switching

### TODOS
- [ ] Validate user configuration for both game and UI settings
- [ ] Handle all the game states inside both ``GameController`` and ``UserInterface``
- [ ] Add animations
- [ ] Optimize local storage (switch to raw bytes for storing ``Grid``'s state)
- [ ] Clean up and unify objects' APIs
- [ ] Document code using [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [ ] Add unit tests

## Installation
As of 07/13/20 this project is still not finished. This means there is no setup wheel yet.

**At least Python ver. 3.7 required.** 
If you want to test out the current version do the following:
```bash
pip install --upgrade pygame
git clone https://github.com/stllfe/python-2048 .
cd python-2048
python -m main
```
**You can edit the** ``config.yaml`` **to change:**
 - grid's dimensions
 - username
 - number of initial tiles
 - winscore *(currently does nothing)*

### CAUTION
Though you may change these properties however you like, do it conciously. Since there is neither validations, nor graphics scaling, you can easily mess up the grid, fonts or just crash the game by setting gridsize to like (100 x 100). 
