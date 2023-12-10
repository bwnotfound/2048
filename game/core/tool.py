import numpy as np


class ToolsBag:
    def __init__(self, size):
        self.size = size
        self.bag = np.zeros(size, dtype=int)  # 默认背包大小与棋盘行列数相同

    # 道具（添加数字）
    def add_tool(self, name):  # 背包的第pos个位置，获得道具编号为name的道具
        indices = np.where(self.bag == 0)
        if len(indices[0]) == 0:
            bag = np.roll(self.bag, -1)
            bag[bag.size - 1] = name
            return bag
        pos = indices[0][0]  # 背包的第一个空位
        self.bag[pos] = name
        return self.bag

    # TODO: 这里的use_tool函数需要修改。需要实际的使用道具（可以传回道具name），同时要明确使用后是不是一定要移除道具
    def use_tool(self, name):  # 使用背包中的某一个道具
        index = np.where(self.bag == name)[0][0]
        for i in range(index, self.bag.size - 1):
            self.bag[i] = self.bag[i + 1]
        self.bag[self.bag.size - 1] = 0
        return self.bag

    def clear_same_tool(self):  # 清理背包中重复的道具，每回合调用
        unique_arr = np.unique(self.bag)
        result = []
        for i in range(len(self.bag)):
            if self.bag[i] in unique_arr:
                result.append(self.bag[i])
                unique_arr = np.delete(unique_arr, np.where(unique_arr == self.bag[i]))
        for i in range(len(self.bag)):
            self.bag[i] = result[i]
        return self.bag

    def get_item_bag(self):
        return self.bag

    def pack_data(self):
        data = self.bag.tolist()
        return data

    def check_data(self, data):
        return True

    def load_data(self, data):
        self.board = np.array(data, dtype=int)
