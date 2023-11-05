# Iterating
1. Using `for i in nums` will give you the values


2. Using `range()` in Loops will give you the index
```py
nums = [10, 20, 30, 40]

# gives you the value
for i in nums:
    print(i)

# gives you the index
for i in range(len(nums)):
    print(i)

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

## Max

```py
max_value = 0
new_value = 5
max_value = max(max_value, new_value)

```