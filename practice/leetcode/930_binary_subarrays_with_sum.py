# Given a binary array nums and an integer goal, return the number of non-empty subarrays with a sum goal.

# A subarray is a contiguous part of the array.


def solution(nums: list[int], goal: int) -> int:
    count = 0
    current_sum = 0
    counts = {}

    # set base case to allow us to count subarrays that start at index 0
    counts[0] = 1

    for num in nums:
        current_sum += num

        if (current_sum - goal) in counts:
            print(counts)
            count += counts[current_sum - goal]

        if current_sum in counts:
            counts[current_sum] += 1
        else:
            counts[current_sum] = 1

    return count

    # prefix_counts[current_sum] += 1


nums1 = [1, 0, 1, 0, 1]
goal1 = 2

nums2 = [0, 0, 0, 0, 0]
goal2 = 0

solution(nums=nums1, goal=goal1)
solution(nums=nums2, goal=goal2)


def solution(nums: list[int], goal: int) -> int:
    current_sum = 0
    count = 0
    start = 0

    for end in range(len(nums)):
        current_sum += nums[end]

        if current_sum > goal:
            current_sum -= nums[start]
            start += 1

        if current_sum == goal:
            print(f"Adding 1 at {end}")
            count += 1

    return count
