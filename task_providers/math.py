import random
from .base import TaskProvider

class MathTaskProvider(TaskProvider):
    @property
    def name(self):
        return "Math Quiz"
    
    @property
    def description(self):
        return f"""Math Practice
        max-factor = {self.max_factor}
        sum-factor = {self.sum_factor}
        
        Solve the problems as quickly as you can!
        Press Enter to begin when ready."""

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--max-factor', type=int, default=12,
                          help='Maximum multiplicand value')
        parser.add_argument('--sum-factor', type=int, default=2,
                          help='Maximum summation order')

    def __init__(self, args):
        self.max_factor = args.max_factor
        self.sum_factor = args.sum_factor

    def generate_task(self):
        if random.choice([1, 2]) == 1:
            a = random.randint(1, self.max_factor)
            b = random.randint(1, self.max_factor)
            return f"{a} × {b} = ", a * b
        else:
            a = random.randint(-10**self.sum_factor, 10**self.sum_factor)
            b = random.randint(1, 10**self.sum_factor)
            if random.choice(["+", "-"]) == "+":
                return f"{a} + {b} = ", a + b
            else:
                return f"{a} - {b} = ", a - b

    def validate_answer(self, user_answer, correct):
        try:
            return int(user_answer) == correct
        except ValueError:
            return False