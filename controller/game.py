import logging

from argparse import Namespace

from common.events import GameReadyEvent, CPUTickEvent, UserMoveEvent, UserRestartEvent, GridUpdateEvent, GameOverEvent, ScoreUpdateEvent, QuitEvent, GameTeardownEvent
from common.errors import MisconfigurationError
from common.mediator import EventManager
from controller.controller import Controller
from model.logic import Logic
from storage.storage import StorageManager

log = logging.getLogger(__name__)


class GameController(Controller):

    def __init__(self,
                 params: Namespace,
                 storage: StorageManager,
                 event_manager: EventManager):

        super().__init__(event_manager)

        self._logic = Logic(params)
        self._params = params
        self._storage = storage

        self._initialized = False
        self._is_finished = False

        self._score = 0
        self._best = 0

    def _initialize(self):
        if self._initialized:
            log.warning("Game can be initialized only once during runtime.")
            return

        checkpoint = self._storage.get(self._params.username)

        if checkpoint:
            self._restore_game(checkpoint)
        else:
            self._setup_logic()

        self._initialized = True

    def _setup_logic(self):
        if not self._logic.setup():
            error = "Invalid number of `start_tiles` provided in config!"
            log.error(error)
            raise MisconfigurationError(error)

    def _restore_game(self, checkpoint):
        self._best = checkpoint.get('best', 0)
        last_game_finished = checkpoint.get('is_finished', False)

        if not last_game_finished:
            state = checkpoint['state']
            self._logic.load_state(state)
            self._score = self._logic.merged_total
        else:
            self._setup_logic()

    def _restart_game(self):
        self._update_best()
        self._score = 0
        self._setup_logic()

    def _teardown(self):
        self._update_best()
        state = self._logic.save_state()
        result = dict(state=state, is_finished=self._is_finished, best=self._best)
        self._storage.set(self._params.username, result)

    def _update_best(self):
        if self._score > self._best:
            self._best = self._score

    def notify(self, event):
        if isinstance(event, CPUTickEvent):
            if not self._initialized:
                self._initialize()
                self.post(GameReadyEvent(grid=self._logic.grid, score=self._score, best=self._best))

        if isinstance(event, UserMoveEvent):
            self._logic.move(event.direction)
            self.post(GridUpdateEvent(grid=self._logic.grid))

            # Check if tiles have merged and update score
            if self._logic.merged_total != self._score:
                self._score = self._logic.merged_total
                self.post(ScoreUpdateEvent(score=self._score, best=self._best))

            # Check if logic can't insert new tiles
            if not self._logic.random_tile():
                # Check if there are any possible moves (expensive)
                if not self._logic.moves_available():
                    self._is_finished = True
                    self.post(GameOverEvent(username=self._params.username, score=self._score, best=self._best))

        if isinstance(event, (QuitEvent, GameTeardownEvent)):
            self._teardown()

        if isinstance(event, UserRestartEvent):
            self._restart_game()
            self.post(GameReadyEvent(grid=self._logic.grid, score=self._score, best=self._best))


