# Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i]
# is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day
# for which this is possible, keep answer[i] == 0 instead.


# solution is a monotonically increasing stack
# time and space complexity of this solution is o(n), we just iterate through
# the input list once and our answer array is the size of the input array n
def solution(temperatures: list[int]) -> list[int]:
    n = len(temperatures)

    # we need an answer for every index, so initialize a list for that and fill
    # in with values of 0
    answer = [0] * n
    stack = []

    # iterate through the input list
    for i in range(n):
        # while we have indexes in the stack and the current temp
        # is greater than the last index in the stack, then we pop that index
        # off the stack and add it to our answer list. `i - idx` is the window
        # which is the # of days we have to wait to get to a higher temp
        while stack and temperatures[i] > temperatures[stack[-1]]:
            idx = stack.pop()
            answer[idx] = i - idx

        # always append the current index to the stack so we can get an answer for it
        # later
        stack.append(i)

    return answer


temperatures1 = [73, 74, 75, 71, 69, 72, 76, 73]
temperatures2 = [30, 40, 50, 60]

solution(temperatures=temperatures1)
solution(temperatures=temperatures2)
