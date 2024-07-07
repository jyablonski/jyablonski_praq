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
