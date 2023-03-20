import sys
import numpy as np
import pandas as pd

my_int = 3
my_large_number = 4343432424

my_str = "hello world"
my_large_str = """
Furthermore, there's just a lot of other stuff to admire about the Xbox Series X. So read on for our fulldfffffffffffffffffffffffffffffffffffffffffffffulldfffffffffffffffffffffffffffffffffffffffffffffulldffffffffffffffffffffffffffffffffffffffffffff
 Xbox Series X review to see whether the new console has been worth the wait, and be sure to check out our guide to the best h
 idden Xbox Series X features(opens in new tab) to get the most out of this console."""

my_list = [1, 2, 3]
my_random_list = [1, "hello world", True, 3.14159, "ghee", "wooo"]
my_large_list = np.array(np.random.randint(2, size=(int(400000), 1)), dtype=bool)

my_df = pd.DataFrame(my_large_list)


sys.getsizeof(my_int)
sys.getsizeof(my_large_number)
sys.getsizeof(my_str)
sys.getsizeof(my_large_str)
sys.getsizeof(my_list)
sys.getsizeof(my_random_list)
sys.getsizeof(my_large_list)
sys.getsizeof(my_df)
