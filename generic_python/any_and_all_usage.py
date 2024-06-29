l1 = [100, 250, 500, 750, 1000]
l2 = [0, None, False]
l3 = [False, False, 3 > 2, False]

# returns true
b1 = any(l1)

# returns False
b2 = any(l2)

# returns true because 1 of the values was > 100
b3 = any(val > 100 for val in l1)

# returns true because 3 > 2 is true
b4 = any(l3)
