# There are several cards arranged in a row, and each card has an associated number of points.
# The points are given in the integer array cardPoints.

# In one step, you can take one card from the beginning or from the end of the row. You have
# to take exactly k cards.

# Your score is the sum of the points of the cards you have taken.

# Given the integer array cardPoints and the integer k, return the maximum score you can
# obtain.

# The key to this problem is recognizing that each valid arrangement of cards we can
# choose is equivalent to removing n - k cards from the middle of the array, where n
# is the length of the array.


def solution(cardPoints: list[int], k: int) -> int:
    n = len(cardPoints)
    total_sum = sum(cardPoints)

    # if k is greater than or equal to n, return the sum of the list
    if k >= n:
        return total_sum

    current_sum = 0
    max_sum = 0
    start = 0

    # we're basically sliding through the list and are able to use the remainder
    # of the total_sum - current_sum to find out what the sum of the edges are

    for end in range(n):
        current_sum += cardPoints[end]

        # we only calculate a new max sum once our window is the size of n - k
        if end - start + 1 == n - k:
            max_sum = max(total_sum - current_sum, max_sum)
            current_sum -= cardPoints[start]
            start += 1

    return max_sum


cardPoints1 = [1, 2, 3, 4, 5, 6, 1]
cardPoints2 = [9, 7, 7, 9, 7, 7, 9]

k1 = 3
k2 = 7

solution(cardPoints=cardPoints1, k=k1)
solution(cardPoints=cardPoints2, k=k2)
