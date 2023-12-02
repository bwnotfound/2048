import toml
from game import GameManager

if __name__ == '__main__':
    config_path = "configs/config.toml"
    game = GameManager(config_path)
    game.start()
