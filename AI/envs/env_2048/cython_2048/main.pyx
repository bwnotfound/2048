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
    cdef float reward = -1.5
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
    cdef int empty_num = 0
    for i in range(size):
        for j in range(size):
            if board[i, j] == 0:
                empty_num += 1
    cdef float ratio = empty_num / (size * size)
    ratio = ratio + 1
    for r in reward_list:
        reward += 1.5 ** r * ratio
    
    return int(reward)