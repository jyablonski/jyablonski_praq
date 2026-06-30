# given list nums of integers:
#   return list answer such that answer[i] is equal to product of all
#   elements except nums[i]
# product of any prefix or suffix of nums is guaranteed to fit in 32-bit integer
# must write o(n) solution without using division

# this problem requires at least 2 loops because you need to multiply the current
# element by all values to the left and to the right of it


# in both loops, you're just updating the result array and then multiplying nums[i]
# onto prefix / suffix
def solution(nums: list[int]) -> list[int]:
    n = len(nums)

    # initialize a new list of length nums with all values set to 1
    answer = [1] * n

    # left to right pass
    # answer[i] is = to prefix because we're setting the value for the first time here
    prefix = 1
    for i in range(n):
        answer[i] = prefix
        prefix *= nums[i]

    print(f"Done with first loop {answer}")

    # right to left pass
    # answer *= suffix here because we need to preserve what was saved in the first loop
    suffix = 1
    for i in reversed(range(n)):
        print(i)
        answer[i] *= suffix
        suffix *= nums[i]

    print(answer)
    return answer


nums1 = [1, 2, 3, 4]
nums2 = [1, -2, 3, 4, -1]
nums3 = [2, 4, 6, 8]

solution(nums=nums1)
solution(nums=nums2)
solution(nums=nums3)
