from input import read
import math
from heap_helperfunctions import insert_min, delete_min, min_heapify, heapify_up

def time_add_30(time):
    """
    Adds 30 minutes to a time in HHMM format and returns the updated time.

    Parameters:
    time (int): Time in HHMM format (e.g., 1345 for 1:45 PM).

    Returns:
    int: Updated time in HHMM format after adding 30 minutes.
    """
    hours = time // 100
    minutes = time % 100
    minutes += 30
    if minutes >= 60:
        minutes -= 60
        hours += 1
    if hours >= 24:
        hours -= 24
    return hours * 100 + minutes

def passengers_increase(passengers):
    increase = 0.2*(passengers)
    new = passengers + math.ceil(increase)
    return new


def build_min_heap(heap):
    """
    Converts a list into a valid min-heap using successive insertions.

    Parameters:
    heap (list): A list of bus records where each record is a tuple:
                 (bus_number, location, time, passengers, capacity).

    Returns:
    None: The input list is transformed into a min-heap in-place.
    """
    temp = []
    for bus in heap:
        insert_min(temp, bus)
    heap.clear()
    heap.extend(temp)


def print_heap(heap):
    """
    Prints the current state of the heap in a readable vertical format.

    Parameters:
    heap (list): The current min-heap of buses.

    Returns:
    None
    """
    print("\nCurrent Heap:")
    for bus in heap:
        print(bus)
    print()


def simulation(filename):
    """
    Simulates the operation of a bus scheduling system using a min-heap.
    
    Each bus is processed based on its scheduled time. Buses with low occupancy
    (< 70%) are delayed by 30 minutes up to 2 times. On the third occurrence,
    they are canceled. Otherwise, buses depart as scheduled.

    Parameters:
    filename (str): Path to the file containing bus schedule data.
                    Each entry should be a tuple:
                    (bus_number, location, time, passengers, capacity)

    Returns:
    None: Outputs simulation results to the console.
    """
    # Step 1: Read data from file
    buses = read(filename)  # Expected format: (bus_number, location, time, passengers, capacity)

    # Step 2: Build a min-heap based on time (3rd element of tuple)
    build_min_heap(buses)

    # Dictionary to track how many times a bus has been delayed
    delay_count = {}

    # Record of actions taken on each bus
    records = []

    print_heap(buses)

    # Step 3: Simulation loop
    while buses:
        current_bus = buses[0]  # Peek at the first bus in the heap (earliest scheduled)
        bus_number, location, time, passengers, capacity = current_bus

        if passengers < 0.7 * capacity:
            # Not enough passengers — consider delay or cancellation
            delay_count[bus_number] = delay_count.get(bus_number, 0) + 1

            if delay_count[bus_number] > 2:
                # Cancel bus after 2 delays
                delete_min(buses)
                msg = f"Bus {bus_number} to {location} at {time} CANCELLED after 2 delays."
                print(msg)
                records.append(msg)
            else:
                # Delay bus by 30 minutes
                new_time = time_add_30(time)
                new_passengers = passengers_increase(passengers)
                delayed_bus = (bus_number, location, new_time, new_passengers, capacity)

                delete_min(buses)
                insert_min(buses, delayed_bus)

                msg = f"Bus {bus_number} to {location} DELAYED to {new_time} (Passengers: {passengers}, Capacity: {capacity})"
                print(msg)
                records.append(msg)

        else:
            # Bus has enough passengers — depart
            delete_min(buses)
            msg = f"Bus {bus_number} to {location} DEPARTED at {time} (Passengers: {passengers}, Capacity: {capacity})"
            print(msg)
            records.append(msg)

        print_heap(buses)

    # Output final summary
    print("\nSimulation complete.")
    print("\n=== FINAL RECORDS ===")
    for record in records:
        print(record)


# Run the simulation
simulation("BUS.txt")
simulation("BUS2.txt")
