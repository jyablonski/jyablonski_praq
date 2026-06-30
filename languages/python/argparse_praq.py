import argparse

# argparse is used to do CLI type stuff.  it allow the user to specify variable values to run a program with
# Run it with `python generic_python/argparse_praq.py 4 4`
# python generic_python/argparse_praq.py --x 4 --y 4
# python generic_python/argparse_praq.py --help

parser = argparse.ArgumentParser(
    prog="Arg Parser Application",
    description="Jacobs Program to do big cool things",
    epilog="Text at the bottom of help",
)

parser.add_argument("--x", type=int, required=True, help="The first value to multiply")
parser.add_argument("--y", type=int, required=True, help="The second value to multiply")
parser.add_argument(
    "--name", type=str, required=False, help="Optional Name to specify", default=""
)


args = parser.parse_args()

product = args.x * args.y
print(f"The Product of Input X {args.x} and Input Y {args.y} is {product} {args.name}")
