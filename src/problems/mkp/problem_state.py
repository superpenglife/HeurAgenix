# This file is generated by generate_problem_state.py.
from src.problems.mkp.components import Solution

import numpy as np


def get_instance_problem_state(instance_data: dict) -> dict:
    """Extract instance problem state from instance data.

    Args:
        instance_data (dict): The dictionary contains the instance data.

    Returns:
        dict: The dictionary contains the instance problem state with:
            - average_profit (float): The average profit of all the items.
            - profit_variance (float): The variance of the profit values of items.
            - average_weight_per_resource (list[float]): The average weight of items for each resource dimension.
            - weight_variance_per_resource (list[float]): The variance of item weights for each resource dimension.
            - capacity_to_weight_ratio (list[float]): The ratio of total capacity to total weight per resource.
            - profit_to_weight_ratio (list[float]): The ratio of profit to weight for each item.

    """
    problem_states = {}

    # Calculate the average profit of items
    problem_states["average_profit"] = np.mean(instance_data["profits"])

    # Calculate the variance of the profit values
    problem_states["profit_variance"] = np.var(instance_data["profits"])

    # Calculate the average weight per resource and weight variance per resource
    problem_states["average_weight_per_resource"] = np.mean(instance_data["weights"], axis=0).tolist()
    problem_states["weight_variance_per_resource"] = np.var(instance_data["weights"], axis=0).tolist()

    # Calculate the capacity to weight ratio for each resource
    total_weights = np.sum(instance_data["weights"], axis=1)
    problem_states["capacity_to_weight_ratio"] = instance_data["capacities"] / total_weights

    # Calculate the profit to weight ratio for each item
    # Prevent division by zero by adding a small epsilon where weights are zero
    epsilon = 1e-10
    weights_with_epsilon = np.where(np.sum(instance_data["weights"], axis=0) == 0, epsilon, np.sum(instance_data["weights"], axis=0))
    problem_states["profit_to_weight_ratio"] = instance_data["profits"] / weights_with_epsilon

    return problem_states

import numpy as np

def get_solution_problem_state(instance_data: dict, solution: Solution) -> dict:
    """Extract solution problem state from instance data and solution.

    Args:
        instance_data (dict): The dictionary contains the instance data.
        solution (Solution): The target solution instance.

    Returns:
        dict: The dictionary contains the solution problem state with:
            - current_solution_value (float): The total profit of items currently included in the knapsack.
            - solution_density (float): The ratio of items included in the knapsack to the total number of items.
            - average_remaining_capacity (float): The average remaining capacity across all resource dimensions.
            - remaining_capacity_variance (float): The variance of the remaining capacities across all resource dimensions.
            - feasibility_ratio (float): The ratio of feasible items to add to the knapsack, calculated against the total remaining items.
            - utilized_capacity_ratio (array-like): The ratio of used capacity to total capacity for each resource dimension.
            - item_profitability_in_solution (float): The average profit of items that are included in the current solution.
    """

    current_weights = np.zeros(instance_data["resource_num"], dtype=float)
    current_profit = 0
    items_in_knapsack = []
    items_not_in_knapsack = []
    feasible_items_to_add = []

    for item_index, included in enumerate(solution.item_inclusion):
        if included:
            items_in_knapsack.append(item_index)
            current_profit += instance_data["profits"][item_index]
            current_weights += instance_data["weights"][:, item_index]
        else:
            items_not_in_knapsack.append(item_index)

    remaining_capacity = instance_data["capacities"] - current_weights

    for item_index in items_not_in_knapsack:
        if np.all(remaining_capacity >= instance_data["weights"][:, item_index]):
            feasible_items_to_add.append(item_index)

    problem_states = {}

    problem_states["current_weights"] = current_weights
    problem_states["remaining_capacity"] = remaining_capacity
    problem_states["items_in_knapsack"] = items_in_knapsack
    problem_states["selected_item_num"] = len(items_in_knapsack)
    problem_states["items_not_in_knapsack"] = items_not_in_knapsack
    problem_states["unselected_item_num"] = len(items_not_in_knapsack)
    problem_states["feasible_items_to_add"] = feasible_items_to_add

    # Calculate the current solution value (total profit)
    problem_states["current_solution_value"] = current_profit

    # Calculate the solution density (ratio of items in the knapsack to total items)
    problem_states["solution_density"] = len(items_in_knapsack) / instance_data["item_num"]

    # Calculate the average remaining capacity across all resources
    problem_states["average_remaining_capacity"] = np.mean(remaining_capacity)

    # Calculate the variance of the remaining capacities
    problem_states["remaining_capacity_variance"] = np.var(remaining_capacity)

    # Calculate the feasibility ratio (feasible items to add vs total remaining items)
    total_remaining_items = instance_data["item_num"] - len(items_in_knapsack)
    problem_states["feasibility_ratio"] = len(feasible_items_to_add) / total_remaining_items if total_remaining_items > 0 else 0

    # Calculate the utilized capacity ratio for each resource
    problem_states["utilized_capacity_ratio"] = current_weights / instance_data["capacities"]

    # Calculate the average profit of items included in the current solution
    included_items = np.array(solution.item_inclusion, dtype=bool)
    included_profits = instance_data["profits"][included_items]
    problem_states["item_profitability_in_solution"] = np.mean(included_profits) if included_items.any() else 0

    return problem_states

def get_observation_problem_state(problem_state: dict) -> dict:
    """Extract core problem state as observation.

    Args:
        problem_state (dict): The dictionary contains the problem state.

    Returns:
        dict: The dictionary contains the core problem state.
    """
    return {
        "selected_item_num": problem_state["selected_item_num"]
    }