# polymorphism allows you to create objects from different classes through the same interface
# below the candle class inherits from the product class, and adds its own `is_scented` attribute


class Product:
    def __init__(
        self,
        product_name: str,
        price: float,
    ) -> None:
        self.product_name = product_name
        self.price = price

    def _print_attrs(self):
        print(f"Product Name: {self.product_name}\nPrice: {self.price}\n")


d = Product("Apple", 5.1)

d._print_attrs()


class Candle(Product):
    def __init__(self, product_name: str, price: float, is_scented: bool):
        super().__init__(product_name, price)
        self.is_scented = is_scented


b = Candle("Cinnamon Swirl", 4.99, True)


b.is_scented
b._print_attrs()
