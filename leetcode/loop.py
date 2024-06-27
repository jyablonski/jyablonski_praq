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
