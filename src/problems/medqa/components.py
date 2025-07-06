from src.problems.base.components import BaseSolution, BaseOperator

class Solution(BaseSolution):
    """The solution for multi-turn medical diagnosis.
    It records collected symptoms and the final diagnosis if any."""
    def __init__(self, collected_symptoms: list[str], diagnosis: str | None = None):
        self.collected_symptoms = collected_symptoms
        self.diagnosis = diagnosis

    def __str__(self) -> str:
        symptom_str = ",".join(self.collected_symptoms)
        return f"symptoms: {symptom_str}\ndiagnosis: {self.diagnosis}"

class AddSymptomOperator(BaseOperator):
    """Add a symptom to the current solution."""
    def __init__(self, symptom: str):
        self.symptom = symptom

    def run(self, solution: Solution) -> Solution:
        if self.symptom not in solution.collected_symptoms:
            new_symptoms = solution.collected_symptoms + [self.symptom]
        else:
            new_symptoms = solution.collected_symptoms
        return Solution(new_symptoms, solution.diagnosis)

class SetDiagnosisOperator(BaseOperator):
    """Set the diagnosis of the solution."""
    def __init__(self, diagnosis: str):
        self.diagnosis = diagnosis

    def run(self, solution: Solution) -> Solution:
        return Solution(solution.collected_symptoms, self.diagnosis)
