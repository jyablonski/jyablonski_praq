class Joker:
    def __init__(self, obj: dict[str, str]):
        self.obj = obj

    def print_vals(self) -> None:
        for key, value in enumerate(self.obj):
            print(f"key {key}, value {value}")

        return None

    def check_vals(self, key: str) -> bool:
        if key in self.obj:
            return True

        return False


c = Joker(obj={"hello": "world"})

c.print_vals()
c.check_vals("hello")
c.check_vals("hello1")


class JokerSingleton:
    _instance = None  # This will hold the one and only instance

    def __new__(cls, obj: dict[str, str]):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.obj = obj
        return cls._instance

    def print_vals(self) -> None:
        for key, value in self.obj.items():
            print(f"key: {key}, value: {value}")

    def check_vals(self, key: str) -> bool:
        return key in self.obj


d = JokerSingleton(obj={"hello": "world"})

d.print_vals()
d.check_vals("hello")
d.check_vals("hello1")
