import time


class Player:
    def __init__(self, name: str, age: int, salary: int):
        self.name = name
        self.age = age
        self.salary = salary
        self.organization = "NBA"

    def vowel_count_in_name(self) -> int:
        vowel_counter = 0
        vowels = set("aeiou")

        for char in self.name.lower():
            if char in vowels:
                vowel_counter += 1

        return vowel_counter

    def name_ends_with_vowel(self) -> bool:
        vowels = set("aeiou")

        if self.name[-1] in vowels:
            return True
        else:
            return False

    def is_salary_even_number(self) -> bool:
        return self.salary % 2 == 0

    def print_attributes(self) -> None:
        print(self.name)
        time.sleep(2)
        print(self.age)
        time.sleep(2)
        print(self.salary)
        time.sleep(2)
        print(self.organization)

    def return_attributes_as_dictionary(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
            "salary": self.salary,
            "organization": self.organization,
        }


b = Player(name="JacOba", age=23, salary=1000000)

b.vowel_count_in_name()
b.name_ends_with_vowel()
b.is_salary_even_number()
b.print_attributes()

attr = b.return_attributes_as_dictionary()

str1 = "jacoba"
