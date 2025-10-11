# In a mystic dungeon, n magicians are standing in a line. Each magician has an attribute that gives you energy.
# Some magicians can give you negative energy, which means taking energy from you.

# You have been cursed in such a way that after absorbing energy from magician i, you will be instantly
# transported to magician (i + k). This process will be repeated until you reach the magician where (i + k) does not exist.

# In other words, you will choose a starting point and then teleport with k jumps until you reach
# the end of the magicians' sequence, absorbing all the energy during the journey.

# You are given an array energy and an integer k. Return the maximum possible energy you can gain.

# Note that when you are reach a magician, you must take energy from them, whether it is negative
# or positive energy.


def solution(energy: list[int], k: int) -> int:
    n = len(energy)
    max_energy = float("-inf")

    # check every index in the energy list, and always reset cur_energy to 0
    for start in range(n):
        cur_energy = 0
        pos = start

        # for each index, we take the energy and increment by pos as long as
        # we're not at the end of the list
        while pos < n:
            cur_energy += energy[pos]
            pos += k

        # always check if we have a new max energy
        max_energy = max(max_energy, cur_energy)

    return max_energy


energy1 = [5, 2, -10, -5, 1]
k1 = 3

energy2 = [-2, -3, -1]
k2 = 2

solution(energy=energy1, k=k1)
solution(energy=energy2, k=k2)


# first try
def solution_old(energy: list[int], k: int) -> int:
    max_energy = energy[0]
    cur_energy = 0
    n = len(energy)
    left = 0

    for i, value in enumerate(energy):
        print(f"On loop {i}")
        cur_energy += value
        while n - left >= k:
            left += k
            # print(f"Adding {energy[left]} to {cur_energy}")
            cur_energy += energy[left]

        max_energy = max(max_energy, cur_energy)
        left = i
        cur_energy = 0

    return max_energy
