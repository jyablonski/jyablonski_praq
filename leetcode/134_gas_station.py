# There are n gas stations along a circular route, where the amount of gas
# at the ith station is gas[i].

# You have a car with an unlimited gas tank and it costs cost[i] of gas to
# travel from the ith station to its next (i + 1)th station. You begin
# the journey with an empty tank at one of the gas stations.

# Given two integer arrays gas and cost, return the starting gas station's'
# 'index if you can travel around the circuit once in the clockwise'
# 'direction, otherwise return -1. If there exists a solution, it is guaranteed to be unique.


# use greedy algorithm because if a segment from station A to B makes you run out of gas,
# no station between A and B can be a valid start and we can continue to the next one
def solution(gas: list[int], cost: list[int]) -> int:
    # if there isnt enough gas along the route, then return -1
    # if there is enough gas, then we're guaranteed to have a valid solution somewhere
    if sum(gas) < sum(cost):
        return -1

    start = 0
    fuel = 0

    # iterate through the gas list
    for i in range(len(gas)):
        # whenever we don't have enough gas to reach the next station, we move our
        # starting gas station to the next station and reset our gas tank.
        if fuel + gas[i] - cost[i] < 0:
            start = i + 1
            fuel = 0
        else:
            # otherwise we have enough gas, so we add the remainer we'll have to our fuel
            fuel += gas[i] - cost[i]

    return start


gas1 = [1, 2, 3, 4, 5]
cost1 = [3, 4, 5, 1, 2]
