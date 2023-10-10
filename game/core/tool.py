import numpy as np
import chessboard as cb

class ToolsBag:
    def __init__(self, size):
        self.size = size
        self.bag = np.zeros(size, dtype=int)  # 默认背包大小与棋盘行列数相同

    # 道具（添加数字）
    def get_tool(self, name):  # 背包的第pos个位置，获得道具编号为name的道具
        indices = np.where(self.bag == 0)
        if len(indices) == 0:
            bag = np.roll(self.bag, -1)
            bag[bag.size - 1] = name
            return bag
        pos = indices[0]  # 背包的第一个空位
        self.bag[pos] = name
        return self.bag

    def use_tool(self, name):  # 使用背包中的某一个道具
        index = np.where(self.bag == name)[0]
        while index < self.bag.size - 1:
            self.bag[index] = self.bag[index + 1]
        self.bag[self.bag.size - 1] = 0
        return self.bag

