# loop through left to right and then right to left to ensure all possible valid substrings
# are considered, especially those that might be cut off by invalid parentheses sequences in one direction.
def solution(s: str) -> int:
    # initialize left + right pointers
    l = 0
    r = 0
    answer = 0
    len_s = len(s)

    for i in range(len_s):
        if s[i] == "(":
            l += 1
        else:
            r += 1

        # if l == r, then a valid substring was found so we can update answer
        if l == r:
            print(f"current answer {answer}, new answer is {max(answer, 2 * l)}")
            answer = max(answer, 2 * l)

        # if this happens, it incicates an invalid substring was found
        if r > l:
            print(f"invalid r > l substring! {r} > {l} at {s[l]}")
            l = 0
            r = 0

    l = 0
    r = 0

    # on the second pass
    for i in range(len_s - 1, -1, -1):
        if s[i] == "(":
            l += 1
        else:
            r += 1

        # if l == r, then a valid substring was found so we can update answer
        if l == r:
            print(f"current answer {answer}, new answer is {max(answer, 2 * l)}")
            answer = max(answer, 2 * l)

        # if this happens, it incicates an invalid substring was found
        if l > r:
            print(f"invalid l > r substring! {l} > {r} at {s[l]}")
            l = 0
            r = 0

    return answer


s1 = "(()"
s2 = ")()())"

solution(s=s1)
solution(s=s2)

# this loops through in reverse order
len_s = 5
for i in range(len_s - 1, -1, -1):
    print(i)
