n = 20

l1 = [0] * (n + 1)
l1[0] = 1
l1[1] = 1

for i in range(2, n + 1):
    l1[i] = l1[i - 1] + l1[i - 2]
