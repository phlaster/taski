import random
import unicodedata
from .base import TaskProvider

class FrenchWordsTaskProvider(TaskProvider):
    WORDS = [
        {'french': 'ville', 'english': 'city', 'alt': ['municipalité']},
        {'french': 'cinéma', 'english': 'cinema', 'alt': ['théâtre']},
        {'french': 'poisson', 'english': 'fish', 'alt': []},
        {'french': 'école', 'english': 'school', 'alt': ['lycée']},
        {'french': 'ordinateur', 'english': 'computer', 'alt': ['PC']},
        {'french': 'maison', 'english': 'house', 'alt': ['domicile', 'logement']},
    ]

    @property
    def name(self):
        return "French Vocabulary Practice"

    @property
    def description(self):
        directions = {
            'e2f': 'English to French',
            'f2e': 'French to English'
        }[self.direction]
        return f"""French Vocabulary Practice ({directions})
        
        Task types enabled: {', '.join(self.active_modes)}
        Accent handling: {'Ignored' if self.ignore_accents else 'Strict'}
        Press Enter to begin when ready."""

    @classmethod
    def add_arguments(cls, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--e2f', action='store_true', help='English to French translation')
        group.add_argument('--f2e', action='store_true', help='French to English translation')
        parser.add_argument('--direct', action='store_true', help='Enable direct translation tasks')
        parser.add_argument('--match', action='store_true', help='Enable matching tasks')
        parser.add_argument('--ignore-accents', action='store_true',
                          help='Treat accented and non-accented versions as identical')

    def __init__(self, args):
        self.direction = 'e2f' if args.e2f else 'f2e'
        self.active_modes = []
        if args.direct: self.active_modes.append('direct')
        if args.match: self.active_modes.append('match')
        if not self.active_modes:
            self.active_modes = ['direct', 'match']  # Default to both if none selected
            
        self.ignore_accents = args.ignore_accents
        self.word_pool = [w for w in self.WORDS]

    def generate_task(self):
        # Select random word and task type
        word = random.choice(self.word_pool)
        task_type = random.choice(self.active_modes)
        
        if task_type == 'direct':
            return self._create_direct_task(word)
        return self._create_match_task(word)

    def _create_direct_task(self, word):
        if self.direction == 'e2f':
            question = f"Translate to French: {word['english']}"
            answers = [word['french']] + word.get('alt', [])
        else:
            question = f"Translate to English: {word['french']}"
            answers = [word['english']] + word.get('alt', [])
            
        return question, answers

    def _create_match_task(self, word):
        # Get correct answer and distractors
        if self.direction == 'e2f':
            target = word['french']
            others = [w['french'] for w in self.WORDS if w['french'] != target]
        else:
            target = word['english']
            others = [w['english'] for w in self.WORDS if w['english'] != target]

        options = random.sample(others, 2)  # Get 2 wrong answers
        options.append(target)
        random.shuffle(options)
        
        correct_index = options.index(target) + 1  # Options are 1-based
        
        question = f"Match translation for:\n{word['french' if self.direction == 'f2e' else 'english']}\n\nOptions:"
        for i, opt in enumerate(options, 1):
            question += f"\n{i}) {opt}"
            
        return question, correct_index

    def validate_answer(self, user_answer, correct):
        if isinstance(correct, list):  # Direct translation task
            possible_answers = [self._normalize(a) for a in correct]
            user_answer = self._normalize(user_answer)
            return user_answer in possible_answers
        
        # Matching task (correct is index)
        try:
            return int(user_answer) == correct
        except ValueError:
            return False

    def _normalize(self, text):
        normalized = text.lower().strip()
        if self.ignore_accents:
            normalized = unicodedata.normalize('NFKD', normalized)
            normalized = ''.join([c for c in normalized 
                                if not unicodedata.combining(c)])
        return normalized