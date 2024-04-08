# bubble sort is an inefficient sorting algortihm
# it's used to teach beginner data structure + algorithm concepts
# 2 for loops; the idea is you swap values next to each other to make sure they're in order
# then you go back to the beginning of the list and repeat the process.  do this over and over until
# every value is in order
def bubble_sort(input_list: list[int]):
    n = len(input_list)

    # when we get to the last element we've finished the sort, so skip that one
    for i in range(n - 1):
        print(
            f"current list is {input_list}; time for a new loop starting at {input_list[i]}"
        )

        for j in range(n - 1):
            # if the left element (that we're on) is > the right element, we have to swap them
            if input_list[j] > input_list[j + 1]:
                print(
                    f"oops! {input_list[j]} is > {input_list[j + 1]}.  have to swap these two"
                )

                # make a tmp because if we dont then we'll just lose the value we're on
                tmp = input_list[j]
                input_list[j] = input_list[j + 1]
                input_list[j + 1] = tmp


my_list = [3, 6, 1, 9, 7, 11, 4]

bubble_sort(my_list)

print(my_list)
