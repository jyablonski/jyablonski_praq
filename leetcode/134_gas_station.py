# There are n gas stations along a circular route, where the amount of gas
# at the ith station is gas[i].

# You have a car with an unlimited gas tank and it costs cost[i] of gas to
# travel from the ith station to its next (i + 1)th station. You begin
# the journey with an empty tank at one of the gas stations.

# Given two integer arrays gas and cost, return the starting gas station's'
# 'index if you can travel around the circuit once in the clockwise'
# 'direction, otherwise return -1. If there exists a solution, it is guaranteed to be unique.


def solution(gas: list[int], cost: list[int]) -> int:
    # initialize some variables to figure out if we can make an entire loop
    total_gas = 0
    total_cost = 0
    current_tank = 0
    start_index = 0

    # iterate through from 0 - len(gas)
    for i in range(len(gas)):
        print(f"on index {i}")
        total_gas += gas[i]
        total_cost += cost[i]
        current_tank += gas[i] - cost[i]

        # this checks if we can make it to the i + 1 station or not
        # if not, then we cant start at the index we're on. so add + 1
        # to it and use the next one and reset current_tank back to 0
        if current_tank < 0:
            print(f"current_tank {current_tank} is less than 0")
            start_index = i + 1
            current_tank = 0

    if total_gas < total_cost:
        return -1
    else:
        return start_index


gas1 = [1, 2, 3, 4, 5]
cost1 = [3, 4, 5, 1, 2]
