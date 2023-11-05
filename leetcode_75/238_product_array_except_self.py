# given list nums of integers:
#   return list answer such that answer[i] is equal to product of all
#   elements except nums[i]
# product of any prefix or suffix of nums is guaranteed to fit in 32-bit integer
# must write o(n) solution without using division
def product(nums: list[int]) -> list[int]:
    nums_length = len(nums)

    # initialize a new list of length nums with all values set to 1
    answer = [1] * nums_length

    # initial value to keep track of the product of elements to the
    # left of the current element during iteration.
    prefix = 1

    for i in range(nums_length):
        answer[i] = prefix
        print(answer)
        prefix *= nums[i]

    # initial value to keep track of the product of elements to the
    # right of the current element during iteration.
    suffix = 1
    for i in range(nums_length - 1, -1, -1):
        answer[i] *= suffix
        print(answer)
        suffix *= nums[i]

    return answer


nums = [1, -2, 3, 4, -1]

solution = product(nums=nums)
print(solution)
