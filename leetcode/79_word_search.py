# Given an m x n grid of characters board and a string word, return true if word exists in the grid.

# The word can be constructed from letters of sequentially adjacent cells,
# where adjacent cells are horizontally or vertically neighboring. The same
# letter cell may not be used more than once.

# this problem is kinda insane ngl


def solution(board: list[list[str]], word: str) -> bool:
    m = len(board)
    n = len(board[0])
    w = len(word)
    if m == 1 and n == 1:
        return board[0][0] == word

    def backtrack(pos, index):
        if index == w:
            return True

        i, j = pos

        if board[i][j] != word[index]:
            return False

        char = board[i][j]  # keep this incase our current solution doesnt end up valid
        board[i][j] = "#"  # mark it as visited

        # this checks up, left, down, and right of the current cell
        for i_off, j_off in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            row, col = i + i_off, j + j_off

            # ensure we're within bounds of the grid and
            if 0 <= row < m and 0 <= col < n:
                if backtrack((row, col), index + 1):
                    return True

        # reset the path if we dont get a solution above
        board[i][j] = char
        return False

    for i in range(m):
        for j in range(n):
            if board[i][j] == word[0]:
                if backtrack((i, j), 0):
                    return True

    return False


board1 = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
word1 = "ABCCED"

solution(board=board1, word=word1)
