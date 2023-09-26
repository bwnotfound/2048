import toml

# from game.ui.windows.menu import main
from game.ui.windows.multi_player import main

if __name__ == '__main__':
    config = toml.load("configs/config.toml")
    main(config)