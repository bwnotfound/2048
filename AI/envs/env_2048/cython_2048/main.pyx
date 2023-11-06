cimport cython

cpdef tuple merge_block_list(list block_list):
    cdef list result = []
    cdef list reward_list = []
    cdef int i = 0
    cdef int length = len(block_list)

    while i < length:
        if i == length - 1:
            result.append(block_list[i])
            break
        if block_list[i] == block_list[i + 1]:
            result.append(block_list[i] + 1)
            reward_list.append(block_list[i] + 1)
            i += 2
        else:
            result.append(block_list[i])
            i += 1

    return result, reward_list

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cpdef list res_empty_element_list(int size, int[:, :] board):
    cdef list result = []
    for i in range(size):
        for j in range(size):
            if board[i, j] == 0:
                result.append((i, j))
    return result

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cpdef int move_board(int dx, int dy, int size, int[:,:]board):
    cdef int block_list_len
    cdef int d, i, j, r
    cdef list block_list
    if dx != 0:
        d = dx
        for i in range(size):
            # 编写2048的核心算法
            block_list = []
            if d == 1:
                for j in range(size - 1, -1, -1):
                    if board[i, j] == 0:
                        continue
                    block_list.append(board[i, j])
                    board[i, j] = 0
            else:
                for j in range(size):
                    if board[i, j] == 0:
                        continue
                    block_list.append(board[i, j])
                    board[i, j] = 0
            if len(block_list) == 0:
                continue
            block_list, reward_list = merge_block_list(block_list)
            block_list_len = len(block_list)
            for j in range(block_list_len):
                if d == -1:
                    board[i, j] = block_list[j]
                else:
                    board[i, size - 1 - j] = block_list[j]
    else:
        d = dy
        for i in range(size):
            # 编写2048的核心算法
            block_list = []
            if d == 1:
                for j in range(size - 1, -1, -1):
                    if board[j, i] == 0:
                        continue
                    block_list.append(board[j, i])
                    board[j, i] = 0
            else:
                for j in range(size):
                    if board[j, i] == 0:
                        continue
                    block_list.append(board[j, i])
                    board[j, i] = 0
            if len(block_list) == 0:
                continue
            block_list, reward_list = merge_block_list(block_list)
            block_list_len = len(block_list)
            for j in range(block_list_len):
                if d == -1:
                    board[j, i] = block_list[j]
                else:
                    board[size - 1 - j, i] = block_list[j]
    # cdef int empty_num = 0
    # for i in range(size):
    #     for j in range(size):
    #         if board[i, j] == 0:
    #             empty_num += 1
    # cdef float ratio = empty_num / (size * size)
    """
        记bn=2**n，an为合成bn产生的价值，rn为合成出bn所产生的总价值
        那么为了适应step的2指数增长，由于不考虑an的时候有r(n+1) = 2*rn，所以我们令r(n+1) = 2*(2*rn)
        首先通过简单计算得知rn = sigma(i,[2,n])(ai*2**(n-i))
        然后通过计算得知，假设a2=c，那么有a3=c*3,an=a3*5**(n-3) [n>=4]
        因此，可以设计奖励函数确保总体增长的线性性
    """
    cdef float reward = 0.0
    cdef float c = 0.01
    for r in reward_list:
        if r == 2:
            reward += c
        elif r >= 3:
            reward += c*3*5**(r-3)
        else:
            raise Exception(f"{r} must >= 2")
        reward += 2.0 ** r
    # reward += (ratio - 0.5) * 0.2
    
    return int(reward)