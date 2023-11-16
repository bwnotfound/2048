import toml
from game import Game
if __name__ == '__main__':
    config_path="configs/config.toml"
    game=Game(config_path)  
    game.start() 
    