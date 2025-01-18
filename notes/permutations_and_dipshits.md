# Permutations and Combinations
Permutations and combinations are fundamental concepts in combinatorics, a branch of mathematics dealing with counting, arrangement, and selection of objects. 

Put simply, permutations are where you're counting the arrangement of objects in a specific order, while you don't have to worry about the order w/ combinations

**Permutations:**
Permutations refer to the arrangement of objects in a specific order. In other words, a permutation is an ordered arrangement of elements. The number of permutations of 'n' distinct objects taken 'r' at a time is denoted by nPr or P(n, r) and is calculated using the formula:

P(n, r) = n! / (n - r)!

Where:
- \( n! \) (read as "n factorial") is the product of all positive integers up to 'n'.
- \( (n - r)! \) represents the factorial of the difference between 'n' and 'r'.

**Combinations:**
Combinations, on the other hand, refer to the selection of objects without considering the order. In combinations, the arrangement of objects is not considered; only the selection matters. The number of combinations of 'n' distinct objects taken 'r' at a time is denoted by nCr or C(n, r) and is calculated using the formula:

C(n, r) = n! / ((r!) * (n - r)!)

Where:
- \( n! \) is the factorial of 'n'.
- \( r! \) is the factorial of 'r'.
- \( (n - r)! \) is the factorial of the difference between 'n' and 'r'.

**Permutations Example:**
Suppose we have a set of 5 distinct letters: {A, B, C, D, E}. We want to find the number of different 3-letter arrangements we can make from these letters.
- n = 5 because we have 5 distinct objects
- r = 3 because we need to take 3 objects at a time

P(5,3)=(5−3)!5!​=2!5!​=2×15×4×3×2×1​=5×4×3=60

So, there are 60 different 3-letter permutations that can be formed from the given set of letters.

**Combinations Example:**
Continuing with the same set of letters {A, B, C, D, E}, let's find the number of different combinations of 3 letters we can choose from this set.

Using the combination formula \( C(n, r) = \frac{{n!}}{{r! \times (n - r)!}} \), where n = 5 (total number of letters) and r = 3 (number of letters to be chosen), we have:

C(5,3)=3!×(5−3)!5!​=3!×2!5!​=3×2×1×2×15×4×3×2×1​=2×15×4​=10

So, there are 10 different combinations of 3 letters that can be chosen from the given set.

In summary, permutations deal with ordered arrangements, while combinations deal with selections without considering the order.

## Duplicates
If we have duplicate elements in the set, such as {A, A, B, C, D, E}, the calculations for permutations and combinations will change slightly due to the presence of repeated elements. Let's consider examples for both permutations and combinations:

**Permutations Example:**
Suppose we want to find the number of different 3-letter permutations we can make from the set {A, A, B, C, D, E}. Here, we have duplicate letters, so the permutations will include arrangements where the same letter is repeated.

Using the permutation formula, we have:
P(6,3) = 6! / (6 - 3)! = 6! / 3! = 6*5*4*3*2*1 / 3*2*1 = 6 * 5 * 4 = 120

However, since there are two identical 'A' letters, each permutation that swaps the positions of these 'A' letters will be counted multiple times. To correct for this, we divide by the factorial of the number of identical items, which is 2 in this case (the number of 'A's), resulting in:
- P(6, 3) / 2! 
- which is equal to 120 / 2
- which is equal to 60

So, there are 60 different 3-letter permutations that can be formed from the given set of letters with duplicates.

**Combinations Example:**
Now, let's find the number of different combinations of 3 letters we can choose from the set {A, A, B, C, D, E}. 

Using the combination formula, we have:
C(6,3)=3!×(6−3)!6!​=3!×3!6!​=3×2×16×5×4​=20

In this case, since combinations don't consider the order, we don't need to adjust for the duplicate 'A' letters.

So, there are 20 different combinations of 3 letters that can be chosen from the given set with duplicates.