import random
import numpy as np
import defines as d


def new_game(n):
    matrix = np.zeros((n, n), dtype=int)
    matrix = add_two(matrix)
    return matrix


def add_two(mat):
    indices = np.where(mat == 0)
    index = random.randint(0, len(indices[0]) - 1)
    mat[indices[0][index], indices[1][index]] = 2
    return mat


def add_four(mat):
    indices = np.where(mat == 0)
    index = random.randint(0, len(indices[0]) - 1)
    mat[indices[0][index], indices[1][index]] = 4
    return mat


def add_eight(mat):
    indices = np.where(mat == 0)
    index = random.randint(0, len(indices[0]) - 1)
    mat[indices[0][index], indices[1][index]] = 8
    return mat

# 道具（添加数字）


####
# 游戏控制
####

# 游戏状态
def game_state(mat, goal):
    # 获胜条件检查
    if np.any(mat == goal):
        return 'win'
    # 空格检查
    if np.any(mat == 0):
        return 'not over'
    # 如果没有空格，检查是否还能进行消除
    if np.any(mat[:-1, :] == mat[1:, :]) or np.any(mat[:, :-1] == mat[:, 1:]):
        return 'not over'
    if np.any(mat[-1, :-1] == mat[-1, 1:]):
        return 'not over'
    if np.any(mat[:-1, -1] == mat[1:, -1]):
        return 'not over'
    return 'lose'


# 检查目前场上的最大数字
def maxnum_check(mat):
    return np.max(mat)


# 计算目前得分
def cal_allnum(mat):
    return np.sum(mat)


# 翻转
def reverse(mat):
    return np.flip(mat, axis=1)


# 转置
def transpose(mat):
    return np.transpose(mat)


# 左移
def cover_up(mat):
    new = np.zeros_like(mat)
    done = False
    for i in range(mat.shape[0]):
        count = 0
        for j in range(mat.shape[1]):
            if mat[i][j] != 0:
                new[i][count] = mat[i][j]
                if j != count:
                    done = True
                count += 1
    return new, done


# 左合并
def merge(mat, done):
    out = 0
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1] - 1):
            if mat[i][j] == mat[i][j + 1] and mat[i][j] != 0:
                mat[i][j] *= 2
                out += mat[i][j]
                mat[i][j + 1] = 0
                done = True
    return mat, done, out


#  待实现：玩家1用wasd对游戏进行控制


# 向上 = 转置+左移+合并+左移+转置
def up(game):
    print("up")
    game = np.transpose(game)
    game, done = cover_up(game)
    game, done, out = merge(game, done)
    game = cover_up(game)[0]
    game = np.transpose(game)
    return game, done, out


# 向下 = 转置翻转+左移+合并+左移+翻转转置
def down(game):
    print("down")
    game = np.flip(np.transpose(game), axis=0)
    game, done = cover_up(game)
    game, done, out = merge(game, done)
    game = cover_up(game)[0]
    game = np.transpose(np.flip(game, axis=0))
    return game, done, out


# 向左 = 左移+合并+左移
def left(game):
    print("left")
    game, done = cover_up(game)
    game, done, out = merge(game, done)
    game = cover_up(game)[0]
    return game, done, out


# 向右 = 翻转+左移+合并+左移+翻转
def right(game):
    print("right")
    game = np.flip(game, axis=1)
    game, done = cover_up(game)
    game, done, out = merge(game, done)
    game = cover_up(game)[0]
    game = np.flip(game, axis=1)
    return game, done, out
