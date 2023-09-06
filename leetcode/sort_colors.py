# given array `nums` with n objects red white or blue, sort them in place so objects of same color are adjacent
# integers 0, 1, 2 represent color red white blue

# bucket sort - sort in linear time bc there are only 3 buckets
# o(n) time solution, o(1) memory solution


# quick sort - partition array into 3 partssssss
def solution(nums: list):
    left_pointer = 0
    right_pointer = len(nums) - 1
    index = 0

    print(1)
    print(f"right pointer is {right_pointer}")

    def swap(i, j):
        print(f"swapping {nums[j]} with {nums[i]}")
        tmp = nums[i]
        nums[i] = nums[j]
        nums[j] = tmp

    while index <= right_pointer:
        if nums[index] == 0:
            swap(left_pointer, index)
            left_pointer += 1

        elif nums[index] == 2:
            swap(index, right_pointer)
            right_pointer -= 1
            index -= 1
        print(f"nums is now {nums}")
        index += 1
    pass


numbers = [0, 1, 2, 0, 1]
solution(numbers)
