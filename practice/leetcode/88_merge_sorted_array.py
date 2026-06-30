# You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, and two
# integers m and n, representing the number of elements in nums1 and nums2 respectively.
# =
# Merge nums1 and nums2 into a single array sorted in non-decreasing order.

# The final sorted array should not be returned by the function, but instead be stored inside
# the array nums1. To accommodate this, nums1 has a length of m + n, where the first m elements
# denote the elements that should be merged, and the last n elements are set to 0 and should be
# ignored. nums2 has a length of n.

# Time: O(m + n) - we process each element exactly once
# Space: O(1) - we only use a constant amount of extra space

# The key insight is working backwards prevents overwriting unprocessed elements,
# making this solution both elegant and efficient!


def solution(nums1, m, nums2, n):
    # index for last element in nums1's non-zero elements
    i = m - 1

    # index for last element in nums2
    j = n - 1

    # index for last position in nums1 array
    k = m + n - 1

    # iterate backwards starting from the end of the array
    while i >= 0 and j >= 0:
        # if nums1 is > nums2, then we set nums1[k] to nums1 and decrement its pter (i)
        if nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1

        # else, we set nums1[k] to the nums2 value and decrement its pter (j)
        else:
            nums1[k] = nums2[j]
            j -= 1

        # always decrement k which is how we're filling up our final nums1 array
        print(f"Nums is now {nums1}")
        k -= 1

    # copy any remaining elements in nums2
    while j >= 0:
        nums1[k] = nums2[j]
        k -= 1
        j -= 1
        print(f"Nums is now {nums1}")


nums1 = [1, 2, 3, 0, 0, 0]
m = 3
nums2 = [2, 5, 6]
n = 3

solution(nums1=nums1, m=m, nums2=nums2, n=n)
