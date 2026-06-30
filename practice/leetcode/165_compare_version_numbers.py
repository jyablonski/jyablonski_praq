# Given two version strings, version1 and version2, compare them. A version string
# consists of revisions separated by dots '.'. The value of the revision is its integer
# conversion ignoring leading zeros.

# To compare version strings, compare their revision values in left-to-right order. If
# one of the version strings has fewer revisions, treat the missing revision values as 0.

# Return the following:

# If version1 < version2, return -1.
# If version1 > version2, return 1.
# Otherwise, return 0.


def solution(version1: str, version2: str) -> int:
    # get the versions into ints to do the comparison
    v1 = [int(x) for x in version1.split(".")]
    v2 = [int(x) for x in version2.split(".")]

    # iterate through the longest version's length:
    for i in range(max(len(v1), len(v2))):
        # pull each versions value at the index we're on
        # if one version has fewer parts, assume missing parts are 0.
        rev1 = v1[i] if i < len(v1) else 0
        rev2 = v2[i] if i < len(v2) else 0

        # do the comparison
        if rev1 < rev2:
            return -1
        elif rev1 > rev2:
            return 1

    # return 0 if all revisions are equal.
    return 0


version1 = "1.2"
version2 = "1.10"


version3 = "1.01"
version4 = "1.001"

version5 = "1.0"
version6 = "1.0.0.0"

solution(version1=version1, version2=version2)
solution(version1=version3, version2=version4)
solution(version1=version5, version2=version6)
