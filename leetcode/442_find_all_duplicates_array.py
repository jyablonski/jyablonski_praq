# Given an integer array nums of length n where all the integers of nums are
# in the range [1, n] and each integer appears at most twice, return an array of all the integers that appears twice.

# You must write an algorithm that runs in O(n) time and uses only constant auxiliary
# space, excluding the space needed to store the output


# it says not to use a hash map beacuse of space but literally what the fuck ever you d umb cunts lmfao
def solution(nums: list[int]) -> list[int]:
    visited = {}

    # iterate through the list and add the element as the key, and the count
    # as the value
    for value in nums:
        if value not in visited:
            visited[value] = 1
        else:
            visited[value] += 1

    # return a list of keys that have a count >= 2
    return [key for key in visited if visited[key] >= 2]


nums1 = [4, 3, 2, 7, 8, 2, 3, 1]
nums2 = [1, 1, 2]
nums3 = [1]

solution(nums=nums1)
solution(nums=nums2)
solution(nums=nums3)


# "proper" solution if you're a dipshit working with imaginary constraints in fairytale land yeet
def solution(nums: list[int]) -> list[int]:
    result = []

    for num in nums:
        index = abs(num) - 1  # convert to 0-based index
        print(index)

        if nums[index] < 0:
            result.append(abs(num))  # we've seen this before
            print(f"New result: {result}")
        else:
            nums[index] = -nums[index]  # mark as seen
            print(f"Just updated {nums[index]}, nums is now {nums}")

    return result
