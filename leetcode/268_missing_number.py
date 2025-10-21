# given array nums containing n distinct numbers in range [0, n] return the only number
# that's missing from the array

# much more intuitive solution, use a set to keep track of all nums in the provided array,
# and then then you just iterate through nums + 1 until you find the 1 not in the input array
def solution_new(nums: list[int]) -> int:
    num_set = set(nums)

    for i in range(len(nums) + 1):
        if i not in num_set:
            return i


def solution(nums: list[int]) -> int:
    length = len(nums)
    result = length
    print(f"starting result: {result}")
    print("\n")

    for i in range(length):
        print(f"before result: {result}")
        print(f"calculating {result} += ({i} - {nums[i]})")
        result += i - nums[i]
        print(f"after result: {result}")
        print("\n")

    return result


# len(nums): This gives the length of the nums list, which represents the
#   total number of elements in the sequence.
# len(nums) + 1: Adding 1 to the length of the list accounts for the fact
#   that the sequence is expected to have one more element than the length
#   of the list.
# len(nums)*(len(nums) + 1) / 2: This expression calculates the sum of
#   the first len(nums) + 1 natural numbers using the formula for the
#   sum of an arithmetic series. The formula is n * (n + 1) / 2, where
#   n is the number of elements.
# sum(nums): This calculates the sum of all the elements in the nums list.


# n * (n + 1) / 2 is the formula for the sum of an arthimethic series
def solution_2(nums: list[int]) -> int:
    missing_element = (len(nums) * (len(nums) + 1) / 2) - sum(nums)

    return int(missing_element)


nums = [3, 7, 1, 4, 5, 6, 0]
solution(nums)
solution_2(nums)

len(nums) * (len(nums) + 1) / 2 - sum(nums)

# result = 7
# result += 0 - 3 = 4
