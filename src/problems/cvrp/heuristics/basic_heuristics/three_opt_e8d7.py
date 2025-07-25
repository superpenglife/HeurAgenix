from src.problems.cvrp.components import *

def three_opt_e8d7(problem_state: dict, algorithm_data: dict, **kwargs) -> tuple[ReverseSegmentOperator, dict]:
    """Implements a 3-opt heuristic algorithm for the Capacitated Vehicle Routing Problem (CVRP).

    Args:
        problem_state (dict): The dictionary contains the problem state. In this algorithm, the following items are necessary:
            - "distance_matrix" (numpy.ndarray): A 2D array representing the distances between nodes.
            - "depot" (int): The index for depot node.
            - "current_solution" (Solution): The current set of routes for all vehicles.
        algorithm_data (dict): Contains the data necessary for this algorithm.

    Returns:
        TwoOptOperator: The operator that represents the best 2-opt move found.
        dict: Updated algorithm dictionary.
    """
    # Retrieve data from problem_state
    distance_matrix = problem_state["distance_matrix"]
    depot = problem_state["depot"]
    current_solution = problem_state["current_solution"]

    # Initialize variables for the best move found
    best_delta = 0
    best_move = None

    # Iterate over all routes to apply the 3-opt move
    for route_index, route in enumerate(current_solution.routes):
        n = len(route)
        if n <= 3:
            continue  # Skip routes that are too short to apply 3-opt

        # Iterate through all combinations of three edges
        for i in range(n):
            for j in range(i + 2, n):
                for k in range(j + 2, n + (1 if i > 0 else 0)):
                    # Calculate the cost difference for the 3-opt move
                    moves, delta = calculate_3opt_moves(distance_matrix, route, i, j, k, depot)

                    # Check if this move is better than the best found so far
                    if delta < best_delta:
                        best_delta = delta
                        best_move = (route_index, moves)

    # If a beneficial move is found, create and return the corresponding operator
    if best_move:
        route_index, segments = best_move
        return ReverseSegmentOperator(route_index, segments), algorithm_data

    # If no beneficial move is found, return None
    return None, algorithm_data

def calculate_3opt_moves(distance_matrix, route, i, j, k, depot):
    """
    Calculate the cost difference for all 3-opt reconnection moves for the given segments and return the best move.
    """
    n = len(route)
    A = route[(i - 1) % n]
    B = route[i % n]
    C = route[(j - 1) % n]
    D = route[j % n]
    E = route[(k - 1) % n]
    F = route[k % n]

    # Calculate the cost of the original segments
    original_cost = distance_matrix[A][B] + distance_matrix[C][D] + distance_matrix[E][F]

    # Initialize the list of all possible new segments and their costs
    possible_moves = [
        (distance_matrix[A][C] + distance_matrix[B][E] + distance_matrix[D][F], [(i % n, (j - 1) % n), (j % n, (k - 1) % n)]),
        (distance_matrix[F][C] + distance_matrix[B][D] + distance_matrix[E][A], [(i % n, (j - 1) % n), (k % n, (i - 1) % n)]),
        (distance_matrix[F][B] + distance_matrix[C][E] + distance_matrix[D][A], [(j % n, (k - 1) % n), (k % n, (i - 1) % n)]),
    ]


    # Find the move with the maximum cost reduction
    best_delta = 0
    best_move = None
    for cost, move in possible_moves:
        delta = cost - original_cost
        if delta < best_delta:
            best_delta = delta
            best_move = move

    # Return the best move and the corresponding cost reduction
    return best_move, best_delta