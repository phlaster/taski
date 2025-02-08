# task_providers/base.py
from abc import ABC, abstractmethod

class TaskProvider(ABC):
    @property
    @abstractmethod
    def name(self):
        """Human-readable name for the quiz type"""
    
    @property
    @abstractmethod
    def description(self):
        """Description to display before quiz starts"""

    @classmethod
    @abstractmethod
    def add_arguments(cls, parser): pass

    @abstractmethod
    def __init__(self, args): pass

    @abstractmethod
    def generate_task(self): pass

    @abstractmethod
    def validate_answer(self, user_answer, correct_answer): pass