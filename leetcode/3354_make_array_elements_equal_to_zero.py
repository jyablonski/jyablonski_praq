# You are given an integer array nums.

# Start by selecting a starting position curr such that nums[curr] == 0, and choose a movement direction of
# either left or right.

# After that, you repeat the following process:

# If curr is out of the range [0, n - 1], this process ends.
# If nums[curr] == 0, move in the current direction by incrementing curr if you are moving right, or
# decrementing curr if you are moving left.
# Else if nums[curr] > 0:
# Decrement nums[curr] by 1.
# Reverse your movement direction (left becomes right and vice versa).
# Take a step in your new direction.
# A selection of the initial position curr and movement direction is considered valid if every element
# in nums becomes 0 by the end of the process.

# Return the number of possible valid selections.


def solution(nums: list[int]) -> int:
    n = len(nums)
    valid_count = 0

    # try each starting position until nums[curr] == 0
    for start_pos in range(n):
        if nums[start_pos] != 0:
            continue

        # then try both directions
        for direction in [1, -1]:
            nums_copy = nums.copy()
            curr = start_pos

            while 0 <= curr < n:
                # if we're equal to 0, move in current direction
                if nums_copy[curr] == 0:
                    curr += direction

                # otherwise, decrement curr and move in the other direction
                # flip direction by doing direction = -direction
                else:
                    nums_copy[curr] -= 1
                    direction = -direction
                    curr += direction

            # if all elements end up at 0, then we increment our res by 1
            if all(x == 0 for x in nums_copy):
                valid_count += 1

    return valid_count


nums1 = [1, 0, 2, 0, 3]
nums2 = [2, 3, 4, 0, 4, 1, 0]

solution(nums=nums1)
solution(nums=nums2)
