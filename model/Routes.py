class Routes:
    """
    A set of routes between different locations
    """
    def __init__(self, distance_matrix, time_matrix):
        self.distance_matrix = distance_matrix
        self.time_matrix = time_matrix

    def distance(self, start_id, end_id):
        # Check if start_id or end_id is not in distance_matrix
        if start_id not in self.distance_matrix or end_id not in self.distance_matrix:
            raise ValueError("Start or end id not in distance matrix")

        # Return the distance between start_id and end_id
        return self.distance_matrix[start_id][end_id]

    def time(self, start_id, end_id):
        # Check if start_id or end_id is not in time_matrix
        if start_id not in self.time_matrix or end_id not in self.time_matrix:
            raise ValueError("Start or end id not in time matrix")

        # Return the time between start_id and end_id
        return self.time_matrix[start_id][end_id]

