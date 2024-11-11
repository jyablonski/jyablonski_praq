# There is a car with capacity empty seats. The vehicle only drives east --> (i.e., it cannot turn around and drive west).

# You are given the integer capacity and an array trips where trips[i] = [numPassengersi, fromi, toi]
# indicates that the ith trip has numPassengersi passengers and the locations to pick them up and drop
# them off are fromi and toi respectively. The locations are given as the number of kilometers due east
# from the car's initial location.

# Return true if it is possible to pick up and drop off all passengers for all the given trips, or false otherwise.


# n log n time complexity
def solution(trips: list[list[int]], capacity: int) -> bool:
    events = []

    # create a new list of tuples. 2x events for each trip to track the pickup and dropoff
    # tuple is in the form of (location, num_passengers)
    # for pickups num_passengers is positive. for dropoffs num_passengers is negative
    for num_passengers, trip_pickup, trip_dropoff in trips:
        events.append((trip_pickup, num_passengers))  # Pickup event
        events.append(
            (trip_dropoff, -num_passengers)
        )  # Dropoff event (negative to reduce passengers)

    print(events)

    # now sort the events so we can perform the subsequent passenger_sum math accurately
    # pickups are adding the location + the passenger count, dropoffs are adding the location and subtracting
    # the passenger count
    events.sort(key=lambda x: (x[0], x[1]))

    print(events)
    current_passenger_sum = 0

    # process each event in order
    for location, passenger_change in events:

        # perform the arithmetic before making the capacity comparison
        current_passenger_sum += passenger_change
        if current_passenger_sum > capacity:
            print(f"Over capacity: {current_passenger_sum} > {capacity}")
            return False

    # return true if we iterate through all trips and havent hit the False condition
    return True


trips1 = [[2, 1, 5], [3, 3, 7]]
capacity1 = 4

trips2 = [[2, 1, 5], [3, 3, 7]]
capacity2 = 5

trips3 = [[9, 3, 4], [9, 1, 7], [4, 2, 4], [7, 4, 5]]
capacity3 = 23

trips4 = [[7, 5, 6], [6, 7, 8], [10, 1, 6]]
capacity4 = 16

solution(trips=trips1, capacity=capacity1)
solution(trips=trips2, capacity=capacity2)
solution(trips=trips3, capacity=capacity3)
solution(trips=trips4, capacity=capacity4)


# my old solution, o^2 time complexity. no me gusta
def old_solution(trips: list[list[int]], capacity: int) -> bool:
    current_passenger_sum = 0
    all_trips_dropoff = {}

    # Sort trips based on their pickup location for easier management
    trips.sort(key=lambda x: x[1])

    for trip in trips:
        num_passengers = trip[0]
        trip_pickup = trip[1]
        trip_dropoff = trip[2]

        # drop off the passengers first if you can
        # this involves finding them, subtracting their sum from current_passenger_sum, and popping the key
        keys_to_pop = [key for key in all_trips_dropoff.keys() if key <= trip_pickup]

        for key in keys_to_pop:
            current_passenger_sum -= all_trips_dropoff[key]
            all_trips_dropoff.pop(key)

        current_passenger_sum += num_passengers

        # run the comparison to see if you have capacity or not
        if current_passenger_sum > capacity:
            print(f"Got {current_passenger_sum} > {capacity}, {all_trips_dropoff}")
            return False

        # Store the number of passengers to be dropped off at the destination
        if trip_dropoff in all_trips_dropoff:
            all_trips_dropoff[trip_dropoff] += num_passengers
        else:
            all_trips_dropoff[trip_dropoff] = num_passengers

        print(current_passenger_sum)
        print(all_trips_dropoff)

    return True
