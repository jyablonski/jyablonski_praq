# array of which the ith element is the price of a given stock on day i
# if you were only able to complete 1 transaction, design algorithm
# to find max profit, and you cannot sell a stock before you buy one.


# the buy and sell prompt should be a clue for 2 pters
# iterate through entire input list using a while loop and the pointers
# right pointer is incremented to the right by 1 every iteration
# only move the left pointer once we find a value that's < the value at the current right index
def solution(nums: list[int]) -> int:
    # left always points to a potential buying day,
    # right alwaysd points to a potential selling day
    left = 0
    right = 1
    max_profit = 0

    while right < len(nums):
        # if we find a scenario where we can buy on day x and sell on day x + y,
        # then calculate the profit and see if it's the max profit we've recorded so far
        if nums[left] < nums[right]:
            profit = nums[right] - nums[left]
            max_profit = max(max_profit, profit)
        else:
            # else if there's no profit available, then
            # move the left pter over to the position of the right one
            # because we cannot make money in this scenario
            left = right

        # always increment the right pointer
        right += 1

    return max_profit


# buy on day 2, sell on day 5 is the most efficient
nums = [7, 1, 5, 3, 6, 4]
nums2 = [16, 15, 14, 13, 11, 5, 3, 1]

solution(nums=nums2)
