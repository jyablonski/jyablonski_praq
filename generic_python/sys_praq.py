import sys

print(sys.version)

# sys.stdout.write is basically a print statement to standard output
sys.stdout.write("jacob")  # 5
sys.stdout.write("jacob two")  # 9

sys.stderr.write("This is stderr text\n")
sys.stderr.flush()
sys.stdout.write("This is stdout text\n")

# total arguments
print(sys.argv[0])
print(sys.argv)
n = len(sys.argv)
print(f"Total arguments passed: {n}")

# shows your CWD as well as the directory your current python binary is at
print(sys.path)

print(sys.modules)

a = 1
print(sys.getrefcount(a))

b = a * 2
print(sys.getrefcount(a))

c = 4
print(sys.getrefcount(a))
