# Given an array of distinct integers `candidates` and a target integer `target`,
# return a list of all unique combinations of candidates where the chosen
# numbers sum to target. You may return the combinations in any order.

# The goal is to find all unique combinations of numbers from candidates
# that sum up to target. Each number can be used unlimited times.


# use a backtracking approach to solve combination sum
# Since each element can be chosen multiple times, the time complexity is O(2^n) in the worst case.
def solution(candidates: list[int], target: int) -> list[list[int]]:
    # the global list of valid combinations
    res = []

    # a temporary list that keeps track of the current solution we're on
    current_sol = []

    n = len(candidates)

    def backtrack(index, current_sum):
        print(f"Building up {current_sol} at index {index} and cur sum {current_sum}")
        # base case 1: if current_sum == target then we've found
        # a valid combination, so store it in res
        if current_sum == target:

            # append a copy of current_sol to res.
            res.append(current_sol[:])
            return

        # base case 2: we went over the target number in the current solution,
        # or we ran out of candidates to try
        if current_sum > target or index == n:
            return

        # OPTION 1: Exclude the current number and move to the next one.
        # This ensures we explore solutions that do not include the current number.
        backtrack(index + 1, current_sum)

        # OPTION 2: Include the current number and keep searching (can reuse it).
        # Stay on the same index to allow reuse.
        # Example: If we have {2, 2} and want to reuse {2} again.
        current_sol.append(candidates[index])
        backtrack(index, current_sum + candidates[index])

        # Undo the last inclusion (backtracking step) before trying the next number.
        # Example: If we find {2, 2, 2} as a solution, we remove the last 2
        # and try {2, 2, x} next (where x is another candidate).
        current_sol.pop()

    backtrack(0, 0)
    return res


candidates1 = [2, 3, 6, 7]
target1 = 7

candidates2 = [2, 3, 5]
target2 = 8

solution(candidates=candidates1, target=target1)
solution(candidates=candidates2, target=target2)


# this example uses candidates1 and target1 above
# Start at index 0 (candidate = 2)

# 1. Skip 2 -> Move to index 1
# 2. Include 2 -> Sum = 2
#    - Include 2 again -> Sum = 4
#      - Include 2 again -> Sum = 6
#        - Include 2 again -> Sum = 8 (invalid, backtrack)
#        - Skip to next candidate (index 1, candidate = 3)
#      - Include 3 -> Sum = 7 (valid)
# 3. Skip 3 -> Move to index 2
# 4. Include 6 -> Sum = 6
#    - Include 6 again -> Sum = 12 (invalid)
#    - Skip to next candidate (index 3, candidate = 7)
# 5. Include 7 -> Sum = 7 (valid)
