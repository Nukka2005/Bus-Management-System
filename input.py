def read(filename):
    """
    Reads bus schedule data from a file and returns a list of bus records.

    Each line in the input file should contain five values separated by whitespace:
    - bus_number (int): Unique identifier for the bus
    - city_code (str): Destination or location code
    - time (int): Scheduled time in HHMM format (e.g., 1345 for 1:45 PM)
    - passengers (int): Number of passengers currently on the bus
    - capacity (int): Maximum passenger capacity of the bus

    Parameters:
    filename (str): Path to the text file containing bus data.

    Returns:
    list of tuples: A list where each element is a tuple containing:
                    (bus_number, city_code, time, passengers, capacity)
    """
    out = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split()  # Remove whitespace and split by spaces
            bus_number = int(line[0])
            city_code = line[1]
            time = int(line[2])
            passengers = int(line[3])
            capacity = int(line[4])
            out.append((bus_number, city_code, time, passengers, capacity))
    return out
