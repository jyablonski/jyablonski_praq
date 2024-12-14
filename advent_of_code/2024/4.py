def find_word_in_grid(word: str) -> list[tuple[int, int]]:
    with open("advent_of_code/2024/day_4_input.txt", "r") as file:
        grid = [line.strip() for line in file.readlines()]

    rows = len(grid)
    cols = len(grid[0])
    word_len = len(word)

    # create a list of tuples representing the direction to move
    directions = [
        (0, 1),  # Horizontal right
        (0, -1),  # Horizontal left
        (1, 0),  # Vertical down
        (-1, 0),  # Vertical up
        (1, 1),  # Diagonal down-right
        (-1, -1),  # Diagonal up-left
        (1, -1),  # Diagonal down-left
        (-1, 1),  # Diagonal up-right
    ]

    def is_valid(r, c):
        """Checks if a cell (r, c) is within the grid bounds."""
        return 0 <= r < rows and 0 <= c < cols

    def search_from(r, c, dir_r, dir_c):
        """
        Checks if the position of the next word is valid and if the character matches.
        If both conditions True, then return True
        """
        for i in range(word_len):
            nr, nc = r + i * dir_r, c + i * dir_c
            if not is_valid(nr, nc) or grid[nr][nc] != word[i]:
                return False
        return True

    positions = []

    # loop through each cell (r, c) in the grid w/ these 2 for loops
    for r in range(rows):
        for c in range(cols):

            # if the cell contains the first character of the word, test all eight directions.

            if grid[r][c] == word[0]:
                for dir_r, dir_c in directions:
                    if search_from(r, c, dir_r, dir_c):
                        positions.append((r, c))

    return positions


result = find_word_in_grid(word="XMAS")

# skipped part 2
