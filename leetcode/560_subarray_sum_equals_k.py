# Given an array of integers nums and an integer k, return the total number of subarrays
# whose sum equals to k.

# A subarray is a contiguous non-empty sequence of elements within an array.

# time and space complexity both of o(n)
def solution(nums: list[int], k: int) -> int:
    count = 0
    prefix_sum = 0

    # Map to store prefix_sum -> frequency
    # Initialize with {0: 1} to handle subarrays starting from index 0
    sum_freq = {0: 1}
    print(f"sum_freq is {sum_freq}")

    for num in nums:
        print(f"processing {num}")
        prefix_sum += num

        # Check if there's a previous prefix sum that when subtracted
        # from current prefix sum gives us k, this would indicate we have
        # a new subarray that equals k
        if (prefix_sum - k) in sum_freq:
            print(f" ----> match found, adding {sum_freq[prefix_sum - k]} to count")
            count += sum_freq[prefix_sum - k]

        sum_freq[prefix_sum] = sum_freq.get(prefix_sum, 0) + 1
        print(f"sum_freq is now {sum_freq}")

    return count


nums1 = [1, 1, 1]
k1 = 2

nums2 = [1, 2, 3]
k2 = 3

solution(nums=nums1, k=k1)
solution(nums=nums2, k=k2)


# first approach
def solution(nums: list[int], k: int) -> int:
    res = 0
    # n = len(nums)
    left = 0
    cur_sum = 0

    for num in nums:
        cur_sum += num

        if cur_sum == k:
            res += 1

        if cur_sum > k:
            while cur_sum > k:
                cur_sum -= nums[left]
                left += 1
    return res
