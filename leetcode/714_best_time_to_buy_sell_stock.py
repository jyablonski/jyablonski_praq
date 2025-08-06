# You are given an array prices where prices[i] is the price of a given stock on the ith day, and an integer fee representing a transaction fee.

# Find the maximum profit you can achieve. You may complete as many transactions as you like, but you need to pay the transaction fee for each transaction.

# Note:

# You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).
# The transaction fee is only charged once for each stock purchase and sale.

# greedy solution w/ o(n) time complexity and o(1) space
def solution(prices: list[int], fee: int) -> int:
    # hold represents us buying & holding a stock
    # cash represents profit after we sell a potential stock and pay the fee
    hold = -prices[0]
    cash = 0

    for price in prices[1:]:
        print(f"Cash is {cash}, hold is {hold} at price {price}")

        # always check if we should keep holding what we already bought?
        # or should we buy *today's* stock (`price`) with our current cash?
        hold = max(hold, cash - price)

        # always check if we can sell today and get more money
        cash = max(cash, hold + price - fee)

    return cash


prices1 = [1, 3, 2, 8, 4, 9]
fee1 = 2

prices2 = [1, 3, 7, 5, 10, 3]
fee2 = 3


solution(prices=prices1, fee=fee1)
solution(prices=prices2, fee=fee2)
