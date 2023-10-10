import random
import numpy as np


class ChessBoard:
    def __init__(self, size=4):
        self.size = size
        self.newstate = 1  # 是否继续生成新数字（在道具中使用）
        self.board = np.zeros((size, size), dtype=int)
        self.board = self.add_new_num(2)
        self.stage = 1  # 根据目前的最大值设计生成数字的概率
        self.score = 0
        self.prizescore = 0  # 奖励分
        self.tool_5_flag = 0
        self.tool_7_flag = 0
        self.specialx = -1
        self.specialy = -1   # 记录工具所需特殊点的坐标

    def add_new_num(self, num=0):
        if num == 0:  # 未指定生成值时，根据stage判断生成值
            s = self.stage
            if s == 1:
                num = random.choices([2, 4], weights=[0.8, 0.2])[0]
            elif s == 2:
                num = random.choices([2, 4, 8], weights=[0.7, 0.25, 0.05])[0]
            elif s == 3:
                num = random.choices([2, 4, 8], weights=[0.6, 0.3, 0.1])[0]
            elif s == 4:
                num = random.choices([2, 4, 8], weights=[0.5, 0.35, 0.15])[0]
            elif s == 5:
                num = random.choices([2, 4, 8, 16], weights=[0.42, 0.38, 0.18, 0.02])[0]
        if self.newstate == 1:
            indices = np.where(self.board == 0)
            index = random.randint(0, len(indices[0]) - 1)
            self.board[indices[0][index], indices[1][index]] = num
        else:
            print("本回合不生成新数字")
            self.newstate = 1
        return self.board

    ####
    # 游戏控制
    ####

    def game_state_check(self, goal):
        """
        游戏状态 均需要每回合调用

        return:
            0: continue(not over)
            1: win
            2: lose
        """
        # 获胜条件检查
        themax = self.max_number()

        # 得分检查
        self.score = self.calc_score()
        if 2 <= themax:
            self.stage = 1
        if 32 <= themax:
            self.stage = 2
        if 256 <= themax:
            self.stage = 3  # 必须按这个顺序，否则道具的功能会出错
        if 1024 <= themax:
            self.stage = 4
        if np.any(self.board == goal):
            return 1

        # 道具功能检查
        if self.tool_5_flag:
            self.tool_5_flag -= 1
            if self.tool_5_flag == 0:   # 奖励回合结束
                self.stage -= 1

        if self.tool_7_flag:
            self.prizescore += (self.board[self.specialx][self.specialy])/self.stage
            self.tool_7_flag -= 1   # 奖励回合数回合-1

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

    # 道具的使用
    def use_tools(self, num):
        print(f"使用道具 {num}")  # 后续将Num替换成具体的名字
        if num == 1:  # 道具1，功能：将现有的棋盘随机打乱
            indices = np.nonzero(self.board)
            pos = self.board[indices]
            random.shuffle(pos)
            self.board[indices] = pos

        elif num == 2:  # 道具2， 功能：复制目前场上的最大数字到一个空位(不超过32)
            if np.any(self.board == 0):
                themax = min(np.max(self.board), 32)
                self.add_new_num(themax)

            else:  # 场上目前没有空位
                print("棋盘已满，无法使用该道具！")

        elif num == 3:  # 道具3， 功能：复制目前场上的最大数字到一个空位(不超过128)  道具2的升级版
            if np.any(self.board == 0):
                themax = min(np.max(self.board), 128)
                self.add_new_num(themax)

            else:  # 场上目前没有空位
                print("棋盘已满，无法使用该道具！")

        elif num == 4:  # 道具4，功能: 下一回合中不生成新的数字（即玩家连续移动两步)
            self.newstate = 0  # 仅当newstate = 1的情况下，生成新数字

        elif num == 5:  # 道具5，功能: 在接下来的若干个回合中，获得新数字的期望值变大
            if self.tool_5_flag:
                print("有一个相同类型的道具正在被使用！")
                return
            self.tool_5_flag = 5   # 5个回合
            self.stage += 1

        elif num == 6:  # 道具6，功能: 根据场上数字的对称程度，获得一个奖励分
            count = 0
            for i in range(self.size):
                for j in range(self.size):
                    if self.board[i][j] == self.board[self.size - i - 1][self.size - j - 1] \
                            and i <= self.size // 2 and j <= self.size // 2:
                        count += 1
            self.prizescore += count*self.stage*20

        elif num == 7:  # 道具7，功能: 随机选择一个奖励格子，根据接下来的3个回合内,根据该格子上的数字获得一个奖励分
            if self.tool_7_flag:
                print("有一个相同类型的道具正在被使用！")
                return
            else:
                self.specialx = random.randint(1, self.size)
                self.specialy = random.randint(1, self.size)
                # TODO：ui界面让这个格子发光
                self.tool_7_flag = 3

        elif num == 8:  # 道具8，功能：随机选择一个奖励格子，使该格子上的值翻倍
            return
            # TODO 具体功能待实现




