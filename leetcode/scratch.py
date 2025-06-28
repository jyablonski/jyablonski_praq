def compute(start_node_id, from_ids, to_ids):
    links = dict(zip(from_ids, to_ids))

    # Rest of the function remains the same
    visited = set()
    current_node = start_node_id

    while current_node in links:
        if current_node in visited:
            return "Loop detected"
        visited.add(current_node)
        print(visited)
        current_node = links[current_node]

    return current_node


# Example usage
print(compute(1, [1, 2, 3, 4], [2, 3, 4, 5]))  # Output: 5
print(compute(1, [1, 2, 3, 4, 5], [2, 3, 4, 5, 3]))  # Output: "Loop detected"


def sub_sequence_in_list(nums: list[int], sub_sequence: list[int]) -> bool:
    l = 0

    for value in nums:
        if value == sub_sequence[l]:
            l += 1
        else:
            l = 0

        if len(sub_sequence) == l:
            return True

    return False


l1 = [2, 5, 3, 11, 7, 15]
sub_sequence_1 = [3, 11, 7]
l2 = [1, 15, 5, 11, 6, 15, 7]
sub_sequence_2 = [15, 5, 10]

sub_sequence_in_list(nums=l1, sub_sequence=sub_sequence_1)
sub_sequence_in_list(nums=l2, sub_sequence=sub_sequence_2)


## increasing subsequence hoe


def solution(nums: list[int]) -> int:
    l = 1
    max_sub = 1

    for i in range(len(nums) - 1):
        if nums[i] < nums[i + 1]:
            l += 1
        else:
            l = 1
        max_sub = max(l, max_sub)

    return max_sub


l1 = [1, 3, 5, 7]
l2 = [11, 3, 5, 17, 24, 19, 20, 21, 1, 2, 3, 1, 56]
l3 = [10, 9, 2, 5, 3, 7, 101, 18]
l4 = [0, 1, 0, 3, 2, 3]


solution(nums=l1)
solution(nums=l2)
solution(nums=l3)
solution(nums=l4)


# this doesn't account for l4, where if we remove the first `3`
# we actually get a longer subsequnence. zzzzz
def solution(nums: list[int]) -> int:
    current_sub = []
    max_sub = []

    for i in range(len(nums)):
        current_sub = []
        current_sub.append(nums[i])
        current_max_num = nums[i]

        l = i + 1
        while l < (len(nums)):
            print(f"checking {nums[l]} vs {current_max_num}")
            if nums[l] > current_max_num:
                current_sub.append(nums[l])
                current_max_num = nums[l]
                print(f"adding {nums[l]} to current_sub {current_sub}")
                l += 1
            else:
                l += 1

        print(f"am i exiting? L IS {l}")
        if len(current_sub) > len(max_sub):
            print(f"new max sub {current_sub}")
            max_sub = current_sub

    print("why are we returning")
    return max_sub


# Given an array of integers nums and an integer k, find the maximum sum of any contiguous
# subarray of size k
def fixed_sliding_window(nums: list[int], k: int) -> int:
    max_sum = 0
    start = 0
    current_sum = 0

    for end in range(len(nums)):
        current_sum += nums[end]

        if end - start + 1 == k:
            max_sum = max(max_sum, current_sum)
            current_sum -= nums[start]
            start += 1

    return max_sum


def nextGreaterElement(nums):
    n = len(nums)

    # create new list of elements of size n and initialize them to -1
    result = [-1] * n
    stack = []

    # iterate through nums and
    for i in range(n):
        # while we have items in the stack and if the current element
        # is greater than the last element in stack, then add that element's index
        # with the current value to result
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result


# same thing, but smaller element rather than large now
def nextSmallerElement(nums):
    n = len(nums)
    result = [-1] * n
    stack = []

    for i in range(n):
        while stack and nums[i] < nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result


# greedy algo
def findContentChildren(greeds, cookies):
    greeds.sort()
    cookies.sort()

    count = 0
    i, j = 0, 0
    while i < len(greeds) and j < len(cookies):
        # current cookie can satisfy current child
        if cookies[j] >= greeds[i]:
            count += 1
            i += 1
        j += 1

    return count


from collections import deque


# breadth first search
def level_order(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        # number of nodes at the current level
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            curr = queue.popleft()
            current_level.append(curr.val)

            if curr.left:
                queue.append(curr.left)
            if curr.right:
                queue.append(curr.right)

        # IMPORTANT
        # we have finished processing all nodes at the current level
        result.append(current_level)

    return result


# level sum
def levelSum(self, root: TreeNode) -> list[int]:
    if not root:
        return []

    nodes = []
    queue = deque([root])

    while queue:
        # start of a new level here
        level_size = len(queue)
        sum_ = 0

        # process all nodes in the current level
        for i in range(level_size):
            node = queue.popleft()
            sum_ += node.val
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        # we are at the end of the level,
        # add the sum of the nodes to the output list
        nodes.append(sum_)

    return nodes
