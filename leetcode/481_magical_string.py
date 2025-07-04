# A magical string s consists of only '1' and '2' and obeys the following rules:

# The string s is magical because concatenating the number of contiguous occurrences of
# characters '1' and '2' generates the string s itself.
# The first few elements of s is s = "1221121221221121122……". If we group the consecutive
# 1's and 2's in s, it will be "1 22 11 2 1 22 1 22 11 2 11 22 ......" and the occurrences
# of 1's or 2's in each group are "1 2 2 1 1 2 1 2 2 1 2 2 ......". You can see that
# the occurrence sequence is s itself.

# Given an integer n, return the number of 1's in the first n number in the magical string s.


def solution(n: int) -> int:
    if n <= 3:
        return 1  # "122" -> only a single 1

    s = [1, 2, 2]
    i = 2
    num = 1

    while len(s) < n:
        times = s[i]
        s.extend([num] * times)
        num = 3 - num
        i += 1

    print(s)
    # need s[:n] because dpeending on the input number, you might loop 11 times
    # and s might have ll elements but n = 10, so you only need the first 10
    return s[:n].count(1)


n1 = 6
n2 = 1

solution(n=n1)
solution(n=n2)
