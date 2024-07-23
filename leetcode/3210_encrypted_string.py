# You are given a string s and an integer k. Encrypt the string using the following algorithm:

# For each character c in s, replace c with the kth character after c in the string (in a cyclic manner).
# Return the encrypted string.

# pretty easy problem. you cant iterate over the existing `s` because you might
# lose ordering and history. so have to create a new one to hold your return value

# then loop through all characters and the trick is to use modulo of i + k to figure out
# whether that sum will go over the length of the input string. you can use modulo
# operator to track that


# if i + k doesnt go over length of s, then just use i + k as the new index
# if i + k does go over length of s, then use the remainer from the modulo as new index
# without this you might run into index out of bounds error during `new_s += s[new_index]`
def solution(s: str, k: int) -> str:
    s_len = len(s)
    new_s = ""

    for i in range(s_len):
        new_index = (i + k) % s_len
        new_s += s[new_index]

    return new_s


s1 = "dart"  # tdar
s2 = "aaa"  # aaa
s3 = "byd"  #

k1 = 3
k2 = 1
k3 = 4

solution(s=s1, k=k1)
solution(s=s2, k=k2)
solution(s=s3, k=k3)
