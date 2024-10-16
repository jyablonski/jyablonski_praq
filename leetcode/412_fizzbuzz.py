num1 = 3
num2 = 5
num3 = 15
num4 = 45


def fizz_buzz(n: int) -> list[str]:
    result_list = []

    for i in range(1, n + 1):
        output = ""
        if i % 3 == 0:
            output += "Fizz"

        if i % 5 == 0:
            output += "Buzz"

        if not output:
            output = str(i)

        result_list.append(output)

    return result_list


fizz_buzz(n=num1)
fizz_buzz(n=num2)
fizz_buzz(n=num3)
fizz_buzz(n=num4)


def fizz_buzz_no_n():
    result_list = []

    for i in range(1, 101):
        output = ""

        if i % 3 == 0:
            output += "Fizz"

        if i % 5 == 0:
            output += "Buzz"

        if not output:
            output = str(i)

        result_list.append(output)

    return result_list


fizz_buzz_no_n()

# the list comprehension way, but meehhhhh
fizzbuzz = [
    "FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else i
    for i in range(1, 101)
]


def fizz_buzz(n: int) -> list[str]:
    return [
        ("Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) or str(i))
        for i in range(1, n + 1)
    ]
