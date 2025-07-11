from src.problems.mkp.components import *

def greedy_by_density_9e8d(problem_state: dict, algorithm_data: dict, **kwargs) -> tuple[AddOperator, dict]:
    """
    Greedy by Density heuristic for the Multidimensional Knapsack Problem.
    This heuristic selects items based on their density, defined as profit divided by the sum of weights across all dimensions.
    It selects the item with the highest density and adds it to the knapsack, repeating the process until no further items can be added without exceeding resource capacities.

    Args:
        problem_state (dict): The dictionary contains the problem state. In this algorithm, the following items are necessary:
            - "profits" (numpy.array): The profit value associated with each item.
            - "weights" (numpy.array): A 2D array where each row represents the resource consumption of an item across all dimensions.
            - "capacities" (numpy.array): The maximum available capacity for each resource dimension.
            - "remaining_capacity" (numpy.array): The remaining capacity for each resource dimension after considering the items included in the current solution.            - "items_not_in_knapsack" (list[int]): A list of item indices that are currently not included in the knapsack.

    Returns:
        AddOperator: The operator to add the selected item to the knapsack.
        dict: Empty dictionary as no algorithm data is updated.
    """
    # Calculate the density for each item not in the knapsack
    densities = []
    for item_index in problem_state["items_not_in_knapsack"]:
        item_profit = problem_state["profits"][item_index]
        item_weight_sum = sum(problem_state["weights"][resource_index][item_index] for resource_index in range(problem_state["resource_num"]))
        item_density = item_profit / item_weight_sum if item_weight_sum > 0 else 0
        densities.append((item_density, item_index))

    # Sort items by density in descending order
    densities.sort(reverse=True, key=lambda x: x[0])

    # Try to add the item with the highest density without violating the constraints
    for density, item_index in densities:
        # Check if adding this item violates any constraints
        if all(problem_state["weights"][resource_index][item_index] <= problem_state["remaining_capacity"][resource_index] for resource_index in range(problem_state["resource_num"])):
            # If it doesn't violate, return the AddOperator for this item
            return AddOperator(item_index), {}

    # If no items can be added without violating constraints, return None
    return None, {}