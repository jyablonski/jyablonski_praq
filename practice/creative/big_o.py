# big o notation is a way to categorize algorithms time or memeory requirements
# based on input.
c = "hello world jacob"

print(len(c))

# o(n), grows linearly
len_sum = 0
for i in c:
    len_sum += 1

print(len_sum)
