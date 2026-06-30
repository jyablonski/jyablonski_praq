class Product:
    def __init__(self, product_name: str, product_price: float):
        self.product_name = product_name
        self.product_price = product_price

    def get_price_old(self):
        return self.product_price

    @property
    def get_price(self):
        return self.product_price


name1 = "Apples"
price1 = 3.99

a1 = Product(product_name=name1, product_price=price1)


# have to call it with parantheses
a1.get_price_old()

# can just call it like an attribute
a1.get_price
