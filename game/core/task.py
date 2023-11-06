import random
import string
import numpy as np


class TaskList:
    def __init__(self, board_size):
        self.status = 0  # 目前是否有已经激活的任务
        self.content = ""
        self.id = 0  # id为0时表示没有任务，为某数字时表示特定任务，同时刻最多只能有一个任务
        self.time = 0  # 剩余回合数
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.size = board_size
        self.num_1 = 0
        self.num_4 = 0
        self.num_5 = 0
        self.give_prize = 0
        self.give_punish = 0

    def update_board(self, newboard):   # UI中需要每回合执行一次
        self.board = newboard.copy()  # 更新当前的棋盘判定状态

    def get_task(self):  # 得到任务
        if self.status == 1:
            print("目前有尚未完成的任务")
            return
        self.status = 1
        self.content, self.id, self.time = self.get_content()
        if self.id == 0:
            self.status = 0
        # ui要显示任务的内容
        print("你获得了如下任务:")
        print(self.content)

    def check_task(self):  # 每回合一次检查任务是否完成
        flag = 0
        if self.status == 0:  # 没有任务
            return
        ###
        # 跟据实际任务（self.id)进行检测,结果存到flag
        if self.id == 1:
            now = np.size(np.nonzero(self.board))   # 目前的剩余数字
            if self.num_1 + 3 - (self.time-1) - now >= 4:
                flag = 1
        elif self.id == 2:
            if self.board[0][self.size-1] == 8:
                flag = 1
        elif self.id == 3:
            if self.board[0][self.size-1] == 16:
                flag = 1
        elif self.id == 4:
            now = np.size(np.nonzero(self.board))
            if self.num_4 + 1 - (self.time-1) - now >= 1:
                flag = 1
        elif self.id == 5:
            if self.time == 1:
                now = np.size(np.nonzero(self.board))
                if now == self.num_5 + 2:
                    flag = 1

        ###
        # 有任务
        if flag == 1:
            self.status = 0
            self.id = 0
            self.time = 0
            self.give_prize = 1
            print("恭喜，任务成功")
            return
        else:
            self.time -= 1
            if self.time == 0:
                self.status = 0
                self.id = 0
                self.content = ""  # 任务失败，时间到
                self.time = 0
                print("很遗憾，任务失败")
                self.give_punish = 1
            return

    def get_content(self):
        a = random.randint(1, 10)
        if a == 1:
            content = "3回合内，在棋盘中完成4次以上的消去过程"
            self.num_1 = np.size(np.nonzero(self.board))
            t = 3
        elif a == 2:
            content = "3回合内，保证某一次移动后棋盘右上角的数字是8"
            t = 3
        elif a == 3:
            content = "3回合内，保证某一次移动后棋盘右上角的数字是16"
            t = 3
        elif a == 4:
            content = "1回合内，完成1次以上的消去过程"
            self.num_4 =  np.size(np.nonzero(self.board))
            t = 1

        elif a == 5:
            content = "2回合内，不进行任何消去操作"
            self.num_5 = np.size(np.nonzero(self.board))
            t = 2
        else:
            a = 0
            content = "目前你没有触发任何任务"
        return content,a,t
