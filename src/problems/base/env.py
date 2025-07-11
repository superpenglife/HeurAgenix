import os
import traceback
from src.problems.base.components import BaseSolution, BaseOperator
from src.util.util import load_function, search_file


class BaseEnv:
    """Base env that stores the static global data, current solution, dynamic state and provide necessary to support algorithm."""
    def __init__(self, data_name: str, problem: str, **kwargs):
        self.problem = problem
        self.data_path = search_file(data_name, problem)
        self.data_ref_name = data_name.split(os.sep)[-1]
        assert self.data_path is not None
        self.instance_data: tuple = self.load_data(self.data_path)
        self.current_solution: BaseSolution = self.init_solution()
        self.algorithm_data: dict = None
        self.recordings: list[tuple] = None
        self.output_dir: str = None
        # Maximum step to constructive a complete solution
        self.construction_steps: int = None
        # Key item in state to compare the solution
        self.key_item: str = None
        # Returns the advantage of the first and second key value 
        # A return value greater than 0 indicates that first is better and the larger the number, the greater the advantage.
        self.compare: callable = None

        problem_state_file = search_file("problem_state.py", problem=self.problem)
        assert problem_state_file is not None, f"Problem state code file {problem_state_file} does not exist"
        self.get_instance_problem_state = load_function(problem_state_file, problem=self.problem, function_name="get_instance_problem_state")
        self.get_solution_problem_state = load_function(problem_state_file, problem=self.problem, function_name="get_solution_problem_state")
        self.problem_state = self.get_problem_state()


    @property
    def is_complete_solution(self) -> bool:
        pass

    @property
    def is_valid_solution(self) -> bool:
        return self.validation_solution(self.current_solution)

    @property
    def continue_run(self) -> bool:
        return True

    @property
    def key_value(self) -> float:
        """Get the key value of the current solution."""
        return self.get_key_value(self.current_solution)

    def get_key_value(self, solution: BaseSolution=None) -> float:
        """Get the key value of the solution."""
        pass

    def reset(self, output_dir: str=None):
        self.current_solution = self.init_solution()
        self.problem_state = self.get_problem_state()
        self.algorithm_data = {}
        self.recordings = []
        if output_dir:
            if os.sep in output_dir:
                self.output_dir = output_dir
            else:
                base_output_dir = os.path.join(os.getenv("AMLT_OUTPUT_DIR"), "..", "..", "output") if os.getenv("AMLT_OUTPUT_DIR") else "output"
                self.output_dir = os.path.join(base_output_dir, self.problem, "result", self.data_ref_name, output_dir)
            os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self, data_path: str) -> dict:
        pass

    def init_solution(self) -> None:
        pass

    def helper_function(self) -> dict:
        return {"get_problem_state": self.get_problem_state, "validation_solution": self.validation_solution}

    def get_problem_state(self, solution: BaseSolution=None) -> dict:
        if solution is None:
            solution = self.current_solution
        instance_problem_state = self.get_instance_problem_state(self.instance_data)
        solution_problem_state = self.get_solution_problem_state(self.instance_data, solution)
        helper_function = self.helper_function()
        problem_state = None
        if solution_problem_state:
            problem_state = {
                **self.instance_data,
                "current_solution": solution,
                self.key_item: self.key_value,
                **helper_function,
                **instance_problem_state,
                **solution_problem_state,
            }
        return problem_state

    def validation_solution(self, solution: BaseSolution=None) -> bool:
        """Check the validation of this solution"""
        pass

    def run_heuristic(self, heuristic: callable, parameters:dict={}, add_record_item: dict={}) -> BaseOperator:
        try:
            operator, delta = heuristic(
                problem_state=self.problem_state,
                algorithm_data=self.algorithm_data,
                **parameters
            )
            if isinstance(operator, BaseOperator):
                self.run_operator(operator)
                self.algorithm_data.update(delta)
            record_item = {"operation_id": len(self.recordings), "heuristic": heuristic.__name__, "operator": operator}
            record_item.update(add_record_item)
            self.recordings.append(record_item)
            return operator
        except Exception as e:
            trace_string = traceback.format_exc()
            print(trace_string)
            return trace_string

    def run_operator(self, operator: BaseOperator) -> bool:
        if isinstance(operator, BaseOperator):
            self.current_solution = operator.run(self.current_solution)
            self.problem_state = self.get_problem_state()
        return operator

    def summarize_env(self) -> str:
        pass

    def __getstate__(self):  
        state = self.__dict__.copy()  
        state.pop("get_instance_problem_state", None)
        state.pop("get_solution_problem_state", None)
        return state  
  
    def __setstate__(self, state):  
        self.__dict__.update(state)  
        self.get_instance_problem_state = load_function("problem_state.py", problem=self.problem, function_name="get_instance_problem_state")
        self.get_solution_problem_state = load_function("problem_state.py", problem=self.problem, function_name="get_solution_problem_state")

    def dump_result(self, content_dict: dict={}, dump_records: list=["operation_id", "operator", "heuristic"], result_file: str="result.txt") -> str:
        content = f"-data: {self.data_path}\n"
        content += f"-current_solution:\n{self.current_solution}\n"
        content += f"-is_complete_solution: {self.is_complete_solution}\n"
        content += f"-is_valid_solution: {self.is_valid_solution}\n"
        content += f"-{self.key_item}: {self.key_value}\n"
        for item, value in content_dict.items():
            content += f"-{item}: {value}\n"
        if dump_records and len(dump_records) > 0 and len(self.recordings) > 0 and len(self.recordings[0].keys()) > 0:
            dump_records = [item for item in dump_records if item in self.recordings[0].keys()]
            content += "-trajectory:\n" + "\t".join(dump_records) + "\n"
            trajectory_str = "\n".join([
                "\t".join([str(recording_item.get(item, "None")) for item in dump_records])
                for recording_item in self.recordings
            ])
            content += trajectory_str

        if self.output_dir != None and result_file != None:
            output_file = os.path.join(self.output_dir, result_file)
            with open(output_file, "w") as file:  
                file.write(content) 
        
        return content

