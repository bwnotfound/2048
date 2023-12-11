import toml
from game import GameManager

if __name__ == '__main__':
    try:
        config_path = "configs/config.toml"
        game = GameManager(config_path)
        game.start()
    except Exception as e:
        print(e)
    input("Press any key to exit...")