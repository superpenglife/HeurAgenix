import json
from src.problems.base.env import BaseEnv
from src.problems.medqa.components import Solution

class Env(BaseEnv):
    """Environment for multi-turn medical diagnosis."""
    def __init__(self, data_name: str, **kwargs):
        super().__init__(data_name, "medqa")
        self.construction_steps = len(self.instance_data.get("symptoms", [])) + 1
        self.key_item = "current_score"
        self.compare = lambda x, y: y - x

    @property
    def is_complete_solution(self) -> bool:
        return self.current_solution.diagnosis is not None

    def load_data(self, data_path: str) -> dict:
        with open(data_path, "r") as f:
            data = json.load(f)
        symptoms = data.get("symptoms", [])
        diagnosis = data.get("diagnosis", None)
        return {"symptoms": symptoms, "diagnosis": diagnosis}

    def init_solution(self) -> Solution:
        return Solution(collected_symptoms=[], diagnosis=None)

    def get_key_value(self, solution: Solution=None) -> float:
        if solution is None:
            solution = self.current_solution
        true_symptoms = set(self.instance_data.get("symptoms", []))
        collected = set(solution.collected_symptoms)
        if len(true_symptoms) > 0:
            symptom_match_ratio = len(true_symptoms & collected) / len(true_symptoms)
        else:
            symptom_match_ratio = 0
        diagnosis_correct = 1 if solution.diagnosis == self.instance_data.get("diagnosis") else 0
        return symptom_match_ratio + diagnosis_correct

    def validation_solution(self, solution: Solution=None) -> bool:
        if solution is None:
            solution = self.current_solution
        if not isinstance(solution, Solution):
            return False
        true_symptoms = set(self.instance_data.get("symptoms", []))
        for s in solution.collected_symptoms:
            if s not in true_symptoms:
                return False
        return True

    def summarize_env(self) -> str:
        return f"symptoms: {self.instance_data.get('symptoms', [])}"
