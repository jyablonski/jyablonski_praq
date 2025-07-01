# Given an array nums with n objects colored red, white, or blue, sort them in-place
# so that objects of the same color are adjacent, with the colors in the order red, white, and blue.

# We will use the integers 0, 1, and 2 to represent the color red, white, and blue, respectively.

# You must solve this problem without using the library's sort function.


def solution(nums: list[int]) -> None:
    n = len(nums)
    left = 0
    right = n - 1
    i = 0

    while i <= right:
        # if we come across 0, then swap it w/ the left pter
        # and increment both `left` and `i` by 1
        if nums[i] == 0:
            nums[i], nums[left] = nums[left], nums[i]
            i += 1
            left += 1

        # if we come across 2, then swap it to the right and
        # decrement the right pter by 1, bc everything to the
        # right of it is already 2 and sorted

        # dont need to increment `i` because we may have just swapped a 0
        # or 1 from the right, so we'll continue the next loop where it is
        elif nums[i] == 2:
            nums[i], nums[right] = nums[right], nums[i]
            right -= 1

        # if we come across a 1, then just increment `i` by 1 bc
        # at the end, everything between left and right will guaranteed
        # to be 1s
        else:
            i += 1

    return nums


nums1 = [2, 0, 2, 1, 1, 0]
nums2 = [2, 0, 1]

solution(nums=nums1)
solution(nums=nums2)
