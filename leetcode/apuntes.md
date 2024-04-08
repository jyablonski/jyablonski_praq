# Iterating
1. Using `for i in nums` will give you the values


2. Using `range()` in Loops will give you the index
```py
nums = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# gives you the value
for value in nums:
    print(i)

# starts from 0, goes to 9
for i in range(10):
    print(i)

# starts from 1, goes to 10
for i in range(1, 11):
    print(i)

l = 0
r = 1

for i in range(0, 9):
    l += 1
    r += 1

# gives you both the index and value at once
for key, value in enumerate(nums):
    print(key, value)

# 2 pointers to loop through & compare
left = 0
right = 1

# use len - 1 when you have 2 pointers so the one in front isn't
for i in range(len(nums) - 1):
    print(f"left element is at {nums[left]} and right is at {nums[right]}")
    left += 1
    right += 1

# start left pointer at left, start right pointer at right most element
left = 0
right = -1

for i in range(len(nums) - 1):
    print(f"left element is at {nums[left]} and right is at {nums[right]}")
    left += 1
    right -= 1


for i in nums:
    for j in nums:
        print(i * j)
```

3. Modulo Operator

``` py
my_value = 15

my_value % 3 # remainder is 0
my_value % 2 # remainder is 1

```

## Max

```py
max_value = 0
new_value = 5
max_value = max(max_value, new_value)

```