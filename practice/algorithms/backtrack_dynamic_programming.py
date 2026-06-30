def calculate_pt_possibilities(
    pt_total: int, pt_options: tuple[int]
) -> list[list[int]]:
    def backtrack(target, start, path):
        # base case 1
        # a valid combo has been found so we can add it and terminate this path
        if target == 0:
            print(f"found unique result, appending {path[:]}")
            results.append(path[:])
            return

        # base case 2
        # terminate path if we dropped below the target
        if target < 0:
            print(f"target {target} would be < 0, terminating")
            return

        for i in range(start, len(pt_options)):
            print(
                f"starting from on attempt {i} for length {pt_options} and path {path}"
            )
            path.append(pt_options[i])
            print(f"adding {pt_options[i]} to current path {path}")

            # Each recursive call moves deeper into the call stack, continuing until one of the base cases is met:

            backtrack(target=target - pt_options[i], start=i, path=path)

            # Once we return from the recursive call, path.pop() is executed, which backtracks and allows the loop to continue with the next possible value.
            path.pop()

    results = []
    backtrack(target=pt_total, start=0, path=[])
    return results


d = calculate_pt_possibilities(4, (1, 2, 3))


def calculate_pt_possibilities(total: int, options: tuple[int]) -> list[list[int]]:
    def backtrack(target, start, path):
        if target == 0:
            results.append(path[:])
            return

        if target < 0:
            return

        for i in range(start, len(options)):
            path.append(options[i])
            backtrack(target=target - options[i], start=i, path=path)

            path.pop()

    results = []
    backtrack(target=total, start=0, path=[])
    return results


### **Dynamic Programming & Backtracking Approach**

# We use **backtracking** to explore all possible combinations that sum up to the target.

# 1. We start with an empty path and iteratively add numbers from `pt_options`, reducing the target accordingly.
# 2. If the target reaches **exactly 0**, we have found a valid combination, and we store it.
# 3. If the target becomes **negative**, the current path is invalid, so we backtrack (remove the last number) and try the next option.
# 4. This process continues until all possibilities are explored.

# #### **How Backtracking Works (Step-by-Step Example for `4, (1,2,3)`)**

# - The first path explored is `[1, 1, 1, 1]`, which sums to `4`, so it’s stored.
# - We **backtrack** by removing the last `1`, returning to `[1, 1, 1]`, and try adding `2`.
#   - This results in `5` (`4 - 5 = -1`), which is invalid, so we return.
# - We then try `[1, 1, 1, 3]`, which results in `6` (`4 - 6 = -2`), also invalid, so we return.

# This process repeats for all possible paths.

# ---

# ### **How `start` is Used**

# - `start` ensures we **only use numbers at or after the current index** in `pt_options`, preventing duplicate permutations in different orders.
# - Each recursive call maintains `start`, ensuring that we **do not revisit previous elements**, keeping the combinations unique.

# For example, in `pt_options = (1, 2, 3)`:
# - If we pick `1` first, `start=0`, meaning we can still pick `1, 2, 3`.
# - If we pick `2` first, `start=1`, meaning we can only pick `2, 3` next.
# - If we pick `3` first, `start=2`, meaning we can only pick `3` next.

# This eliminates duplicate sets like `[2,1,1]` and `[1,2,1]`, keeping only unique combinations.
