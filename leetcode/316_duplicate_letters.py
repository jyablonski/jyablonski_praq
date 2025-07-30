# Given a string s, remove duplicate letters so that every letter appears once and only once.
# You must make sure your result is the smallest in lexicographical order among all possible results.


def solution(s: str) -> str:
    # Store the last index where each character appears in the string
    last_index = {c: i for i, c in enumerate(s)}
    stack = []
    seen = set()

    for i, c in enumerate(s):
        # if the char is already in our set, skip it
        if c in seen:
            continue

        # remove characters from the stack if:
        # 1. the stack is not empty
        # 2. the current character is smaller (lex order) than the last one in the stack
        # 3. the last character in the stack will appear again later (so it's safe to remove)
        while stack and c < stack[-1] and last_index[stack[-1]] > i:
            removed = stack.pop()
            seen.remove(removed)

        # always add the character to stack and the set
        stack.append(c)
        seen.add(c)

    # end result will be the string in lexicographical order, so just return it as a str
    return "".join(stack)


s1 = "bcabc"
s2 = ""

# this a great example of the why the while loop is needed
# our stack will start with stack = ["b", "c"], but these values appear later on
# so once we reach "a" and we find out that both b and c will appear later on,
# we remove them from stack so stack starts with only "a"
s3 = "bcabc"

solution(s=s1)
solution(s=s2)
solution(s=s3)


# this lexicogprahgical bullshit is so fucking annoying
def solution(s: str) -> str:
    chars = set(s)
    sorted_chars = sorted(chars, key=lambda x: x[0])

    return "".join(sorted_chars)
