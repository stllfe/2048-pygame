import curses

from argparse import Namespace
from curses import initscr
from logic import Logic


class Game:

    def __init__(self, params: Namespace):
        self.best = 0
        self.running = False
        self.screen = None

        self.username = params.username
        self.logic = Logic(params)

    def run(self):
        self.screen = initscr()
        self.screen.idlok(True)
        self.screen.keypad(True)

        curses.cbreak()
        curses.noecho()

        self.running = True
        self.update()

        try:
            while self.running:
                key = self.screen.getch()

                if key == ord('q'):
                    self.running = False

                if key == curses.KEY_LEFT:
                    self.logic.left()
                if key == curses.KEY_RIGHT:
                    self.logic.right()
                if key == curses.KEY_UP:
                    self.logic.up()
                if key == curses.KEY_DOWN:
                    self.logic.down()

                self.update()
        except KeyboardInterrupt:
            self.running = False
        finally:
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def update(self):
        self.screen.clear()
        self.screen.addstr(0, 0, f'score: {self.logic.score}')
        self.screen.addstr(1, 0, f'best: {self.best}')
        self.screen.addstr(3, 0, str(self.logic.grid))
        self.screen.refresh()
