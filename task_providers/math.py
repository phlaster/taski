# task_providers/math.py
import random
from .base import TaskProvider

class MultiplicationTaskProvider(TaskProvider):
    @property
    def name(self):
        return "Multiplication Quiz"
    
    @property
    def description(self):
        return f"""Multiplication Practice (Up to {self.max_factor}x{self.max_factor})
        
        Solve the problems as quickly as you can!
        Press Enter to begin when ready."""

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--max-factor', type=int, default=12,
                          help='Maximum multiplicand value')

    def __init__(self, args):
        self.max_factor = args.max_factor

    def generate_task(self):
        a = random.randint(1, self.max_factor)
        b = random.randint(1, self.max_factor)
        return f"{a} × {b} = ", a * b

    def validate_answer(self, user_answer, correct):
        try:
            return int(user_answer) == correct
        except ValueError:
            return False