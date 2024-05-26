# all of these values will meet the `if not ` condition below,
# and run the print statement
values = [None, False, "", 0, 0.0, [], (), {}, set(), range(0)]

for i, z in enumerate(values, start=1):
    if not z:
        print(f"hello v{i}")
