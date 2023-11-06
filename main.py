import toml
from game import Game
if __name__ == '__main__':
    config = toml.load("configs/config.toml")
    game=Game(config)  
    game.start() 