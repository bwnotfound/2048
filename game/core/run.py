import pygame
import random
import logics as l
import defines as d
import numpy as np

def gen():
    return random.randint(0, d.GRID_LEN - 1)


class GameGrid:
    def __init__(self):
        pygame.init()
        self.goal = d.GOAL
        self.step = 0
        self.screen = pygame.display.set_mode((400, 400))
        self.clock = pygame.time.Clock()
        self.score = 0
        pygame.display.set_caption('2048')
        self.commands = {
            d.KEY_UP: l.up,
            d.KEY_DOWN: l.down,
            d.KEY_LEFT: l.left,
            d.KEY_RIGHT: l.right,
            d.KEY_UP_ALT1: l.up,
            d.KEY_DOWN_ALT1: l.down,
            d.KEY_LEFT_ALT1: l.left,
            d.KEY_RIGHT_ALT1: l.right,
            d.KEY_UP_ALT2: l.up,
            d.KEY_DOWN_ALT2: l.down,
            d.KEY_LEFT_ALT2: l.left,
            d.KEY_RIGHT_ALT2: l.right,
        }

        self.grid_cells = []
        self.matrix = l.new_game(d.GRID_LEN)
        self.history_matrixs = []
        self.update_grid_cells()
        self.item_num = {}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.key_down(event)

    # def init_grid(self):
    #     # 背景
    #     background = pygame.Surface((d.SIZE, d.SIZE))
    #     background.fill(d.BACKGROUND_COLOR_GAME)
    #     self.screen.blit(background, (0, 0))
    #     # 添加单元格
    #     for i in range(d.GRID_LEN):
    #         grid_row = []
    #         for j in range(d.GRID_LEN):
    #             cell = pygame.Surface((d.SIZE / d.GRID_LEN, d.SIZE / d.GRID_LEN))
    #             cell.fill(d.BACKGROUND_COLOR_CELL_EMPTY)
    #             self.screen.blit(cell, (j * d.SIZE / d.GRID_LEN, i * d.SIZE / d.GRID_LEN))
    #             number = pygame.Surface((6, 3))
    #             number.fill(d.BACKGROUND_COLOR_CELL_EMPTY)
    #             font = pygame.font.Font(None, d.FONT_SIZE)
    #             text = font.render("", True, d.FONT_COLOR)
    #             number.blit(text, (0, 0))
    #             self.screen.blit(number, (j * d.SIZE / d.GRID_LEN + 3, i * d.SIZE / d.GRID_LEN + 3))
    #             grid_row.append(number)
    #         self.grid_cells.append(grid_row)

    # 更新棋盘
    def update_grid_cells(self):
        #global cell_color
        for i in range(d.GRID_LEN):
            for j in range(d.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    number_text = ""
                else:
                    number_text = str(new_number)
                cell_rect = pygame.Rect(
                    j * (d.SIZE / d.GRID_LEN),
                    i * (d.SIZE / d.GRID_LEN),
                    d.SIZE / d.GRID_LEN,
                    d.SIZE / d.GRID_LEN
                )   # 尺寸
                pygame.draw.rect(self.screen, cell_rect)
                font = pygame.font.Font(None, d.FONT_SIZE)
                text_surface = font.render(number_text, True, d.FONT_COLOR)
                text_rect = text_surface.get_rect(center=cell_rect.center)
                self.screen.blit(text_surface, text_rect)
        pygame.display.update()

    # 接受接盘输入
    def key_down(self, event):
        key = event.key
        if key == pygame.K_ESCAPE:
            exit()
        if key == pygame.K_BACKSPACE and len(self.history_matrixs) > 1:
            self.matrix = self.history_matrixs.pop()
            self.update_grid_cells()
            print('back on step total step:', len(self.history_matrixs))
        elif key in self.commands:
            self.matrix, done, scoreget = self.commands[key]
            if done:
                self.step += 1
                self.score += scoreget
                max_number = l.maxnum_check(self.matrix)
                if max_number < 16:
                    self.matrix = l.add_two(self.matrix)
                elif 16 <= max_number < 128:
                    if random.random() < d.PRO_16_4:
                        self.matrix = l.add_two(self.matrix)
                    else:
                        self.matrix = l.add_four(self.matrix)
                else:  # max_number >= 128
                    random_number = random.random()
                    if random_number < d.PRO_128_4:
                        self.matrix = l.add_two(self.matrix)
                    elif random_number < d.PRO_128_8:
                        self.matrix = l.add_four(self.matrix)
                    else:
                        self.matrix = l.add_eight(self.matrix)
                print(f"step:{self.step},score:{self.score}")
                # record last move
                self.history_matrixs.append(np.copy(self.matrix))
                self.update_grid_cells()  # 保存

            #  结算动画  修改  ----
            # if l.game_state(self.matrix, self.goal) == 'win':
            #     self.grid_cells[1][1].configure(text="You", bg=d.BACKGROUND_COLOR_CELL_EMPTY)
            #     self.grid_cells[1][2].configure(text="Win!", bg=d.BACKGROUND_COLOR_CELL_EMPTY)
            # if l.game_state(self.matrix, self.goal) == 'lose':
            #     self.grid_cells[1][1].configure(text="You", bg=d.BACKGROUND_COLOR_CELL_EMPTY)
            #     self.grid_cells[1][2].configure(text="Lose!", bg=d.BACKGROUND_COLOR_CELL_EMPTY)


game_grid = GameGrid()
