# A school is trying to take an annual photo of all the students. The students are asked to stand in a single
# file line in non-decreasing order by height. Let this ordering be represented by the integer array expected where
# expected[i] is the expected height of the ith student in line.

# You are given an integer array heights representing the current order that the students are standing in.
# Each heights[i] is the height of the ith student in line (0-indexed).

# Return the number of indices where heights[i] != expected[i].


def solution(heights: list[int]) -> int:
    mismatches = []
    sorted_heights = sorted(heights)
    height_matches = zip(heights, sorted_heights)

    for index, (original_value, sorted_value) in enumerate(height_matches):
        if original_value != sorted_value:
            mismatches.append(index)

    print(mismatches)
    return len(mismatches)


heights1 = [1, 1, 4, 2, 1, 3]
heights2 = [5, 1, 2, 3, 4]
heights3 = [1, 2, 3, 4, 5]

solution(heights=heights1)
solution(heights=heights2)
solution(heights=heights3)


sorted_heights = sorted(heights1)
height_matches = zip(heights1, sorted_heights)

for index, (original, sorted_height) in enumerate(height_matches):
    print(f"Index: {index}, Original: {original}, Sorted: {sorted_height}")
