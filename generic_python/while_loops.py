nums = [10, 2323, 2525, 131, 1554, 1322, 1]

index = 0

while index < 5:
    print(nums[index])
    index += 1

left = 0
right = 1


def find_when_stops_increasing(nums: list[int]) -> list[int]:
    for key, value in enumerate(nums):
        if nums[key + 1] < nums[key]:
            return key
    return -1


nums = [1, 2, 3, 4, 7, 9]
solution = find_when_stops_increasing(nums)


def find_when_stops_increasing(nums: list[int]) -> int:
    for i in range(len(nums) - 1):
        print(i)
        if nums[i + 1] < nums[i]:
            return i
    return (
        -1
    )  # If the list is entirely increasing, return -1 to indicate no stop in the increase.


# Example usage:
nums = [1, 2, 3, 5, 4, 7, 9]
result = find_when_stops_increasing(nums)
print(result)


elements = [100, 200, 300, 400, 500]

# use this to get index for 0 - 4
for i in range(len(elements)):
    print(i)

# use this to get index 0 - 3 - useful if you're ever using 2+ pointers
# with elements[i + 1] > elements[i] shit
for i in range(len(elements) - 1):
    print(i)
