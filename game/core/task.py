import string
import numpy as np


class TaskList:
    def __init__(self, board_size):
        self.status = 0  # 目前是否有已经激活的任务
        self.content = ""
        self.id = 0  # id为0时表示没有任务，为某数字时表示特定任务，同时刻最多只能有一个任务
        self.time = 0  # 剩余回合数
        self.board = np.zeros((board_size, board_size), dtype=int)

    def update_board(self, newboard):
        self.board = newboard.copy()  # 更新当前的棋盘判定状态

    def get_task(self, id, time, content):  # 得到任务
        self.status = 1
        self.id = id
        self.time = time
        self.content = content
        # ui要显示任务的内容

    def check_task(self):  # 每回合一次检查任务是否完成
        flag = 0
        if self.status == 0:  # 没有任务
            return
        ###
        # 跟据实际任务（self.id)进行检测,结果存到flag

        ###

        if flag == 1:
            self.status = 0
            self.id = 0
            self.content = ""
            self.time = 0
            # 触发奖励机制
            return
        else:
            self.time -= 1
            if self.time == 0:
                self.status = 0
                self.id = 0
                self.content = ""  # 任务失败，时间到
                self.time = 0
            return
