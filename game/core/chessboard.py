import random
import numpy as np


class ChessBoard:
    def __init__(self, size=4):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.add_new_num(2)

    def add_new_num(self, num):
        indices = np.where(self.board == 0)
        index = random.randint(0, len(indices[0]) - 1)
        self.board[indices[0][index], indices[1][index]] = num
        return self.board

    ####
    # 游戏控制
    ####

    def game_state_check(self, goal):
        r"""
        游戏状态 均需要每回合调用

        return:
            0: continue(not over)
            1: win
            2: lose
        """
        # 获胜条件检查
        if np.any(self.board == goal):
            return 1
        # 空格检查
        if np.any(self.board == 0):
            return 0
        # 如果没有空格，检查是否还能进行消除
        if np.any(self.board[:-1, :] == self.board[1:, :]) or np.any(
            self.board[:, :-1] == self.board[:, 1:]
        ):
            return 0
        return 2

    # 检查目前场上的最大数字
    def max_number(self):
        return np.max(self.board)

    # 计算目前得分
    def calc_score(self):
        return np.sum(self.board)

    # 游戏状态控制
    # 水平翻转
    def h_reverse(self):
        return np.flip(self.board, axis=1)

    # 转置
    def transpose(self):
        return np.transpose(self.board)

    # 左移
    def cover_up(self):
        new = np.zeros_like(self.board)
        done = False
        for i in range(self.board.shape[0]):
            count = 0
            for j in range(self.board.shape[1]):
                if self.board[i][j] != 0:
                    new[i][count] = self.board[i][j]
                    if j != count:
                        done = True
                    count += 1
        return new, done

    # 左合并
    def merge(self):
        point_get = 0
        done = False
        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1] - 1):
                if self.board[i][j] == self.board[i][j + 1] and self.board[i][j] != 0:
                    self.board[i][j] *= 2
                    point_get += self.board[i][j]
                    self.board[i][j + 1] = 0
                    done = True
        return self.board, done, point_get

    #  待实现：玩家1用wasd对游戏进行控制

    # 向上 = 转置+左移+合并+左移+转置
    def up(self):
        print("up")
        self.board = np.transpose(self.board)
        self.board, done = self.cover_up()
        self.board, done, point_get = self.merge()
        self.board = self.cover_up()[0]
        self.board = np.transpose()
        return self.board, done, point_get

    # 向下 = 转置翻转+左移+合并+左移+翻转转置
    def down(self):
        print("down")
        self.board = np.flip(np.transpose(self.board), axis=0)
        self.board, done = self.cover_up()
        self.board, done, point_get = self.merge()
        self.board = self.cover_up()[0]
        self.board = np.transpose(np.flip(self.board, axis=0))
        return self.board, done, point_get

    # 向左 = 左移+合并+左移
    def left(self):
        print("left")
        self.board, done = self.cover_up()
        self.board, done, point_get = self.merge()
        self.board = self.cover_up()[0]
        return self.board, done, point_get

    # 向右 = 翻转+左移+合并+左移+翻转
    def right(self):
        print("right")
        self.board = np.flip(self.board, axis=1)
        self.board, done = self.cover_up()
        self.board, done, point_get = self.merge()
        self.board = self.cover_up()[0]
        self.board = np.flip(self.board, axis=1)
        return self.board, done, point_get
