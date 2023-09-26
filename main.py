import toml

from game.ui.windows.menu import main

if __name__ == '__main__':
    config = toml.load("configs/config.toml")
    main(config)