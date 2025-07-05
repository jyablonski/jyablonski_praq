def solution(nums: list[int]) -> int:
    nums = sorted(nums)

    return nums[len(nums) // 2]


nums = [3, 2, 3]
nums2 = [2, 2, 1, 1, 1, 2, 2]
nums3 = [1, 1, 1, 2, 3, 4, 5, 6, 7]

solution(nums)
solution(nums2)
solution(nums3)


# vanilla way of doing it
def majorityElement(self, nums: list[int]) -> int:
    counts = {}

    for value in nums:
        if value not in counts:
            counts[value] = 1
        else:
            counts[value] += 1

    counts_sorted = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    return counts_sorted[0][0]


# other solution w/ no dictionary
def majorityElement(self, nums: list[int]) -> int:
    ans = -1
    count = 0

    for num in nums:
        if count == 0:
            ans = num

        if ans == num:
            count += 1
        else:
            count -= 1

    return count
