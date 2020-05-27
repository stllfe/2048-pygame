import yaml

from argparse import Namespace
from game import Game


if __name__ == "__main__":
    default = yaml.safe_load(open('default.yaml', 'r'))
    params = Namespace(**default)
    game = Game(params)
    game.run()
