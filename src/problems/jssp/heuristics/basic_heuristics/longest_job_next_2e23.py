from src.problems.jssp.components import Solution, AdvanceOperator

def longest_job_next_2e23(problem_state: dict, algorithm_data: dict, **kwargs) -> tuple[AdvanceOperator, dict]:
    """Longest Job Next heuristic for JSSP.
    
    Prioritizes the job with the longest total processing time remaining. It uses the
    AdvanceOperator to schedule the next operation for the job with the maximum
    remaining processing time.

    Args:
        problem_state (dict): The dictionary contains the problem state. In this algorithm, the following items are necessary:
            - "job_operation_time" (numpy.ndarray):  The time cost for each operation in each job.
            - "job_num" (int): The total number of jobs in the problem.
            - "unfinished_jobs" (list[int]): List of all unfinished jobs.
            - "job_operation_index" (list[int]): The index of the next operation to be scheduled for each job.
            - "current_solution" (Solution): The current state of the job sequences on each machine.
            
        algorithm_data (dict): Contains data necessary for this algorithm.
            (No specific data needed for this algorithm; can be omitted or passed as an empty dict)
        
        **kwargs: Additional hyperparameters (not used in this algorithm).

    Returns:
        (AdvanceOperator): The operator to advance the job with the longest processing time remaining.
        (dict): Empty dictionary as no algorithm data is updated.
    """
    # Extract necessary data from the global and state dictionaries.
    job_operation_time = problem_state["job_operation_time"]
    unfinished_jobs = problem_state["unfinished_jobs"]
    job_operation_index = problem_state["job_operation_index"]
    
    # Check if there are any unfinished jobs. If not, return None.
    if not unfinished_jobs:
        return None, {}
    
    # Calculate remaining processing time for each unfinished job.
    remaining_times = {
        job_id: sum(job_operation_time[job_id][index:])
        for job_id, index in enumerate(job_operation_index) if job_id in unfinished_jobs
    }
    
    # Find the job with the maximum remaining processing time.
    job_id_to_schedule = max(remaining_times, key=remaining_times.get)
    
    # Create and return the AdvanceOperator for the job with the longest job next.
    advance_op = AdvanceOperator(job_id=job_id_to_schedule)
    
    return advance_op, {}