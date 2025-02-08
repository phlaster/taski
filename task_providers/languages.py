import random
import unicodedata
from .base import TaskProvider

class FrenchWordsTaskProvider(TaskProvider):
    E2F_VOCAB = {
        'city': ['ville', 'municipalité'],
        'cinema': ['cinéma'],
        'fish': ['poisson'],
        'school': ['école', 'lycée'],
        'computer': ['ordinateur', 'PC'],
        'house': ['maison', 'logement', 'domicile']
    }

    F2E_VOCAB = {
        'ville': ['city', 'town'],
        'cinéma': ['cinema', 'movie theater'],
        'poisson': ['fish'],
        'école': ['school'],
        'ordinateur': ['computer'],
        'maison': ['house', 'home']
    }

    @property
    def name(self):
        return "French Vocabulary Practice"

    @property
    def description(self):
        direction = "English to French" if self.direction == 'e2f' else "French to English"
        return f"""French Vocabulary Practice ({direction})
        
        Task types enabled: {', '.join(self.active_modes)}
        Accent handling: {'Ignored' if self.ignore_accents else 'Strict'}
        Total words in vocabulary: {len(self.current_vocab)}
        Press Enter to begin when ready."""

    @classmethod
    def add_arguments(cls, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--e2f', action='store_true', help='English to French translation')
        group.add_argument('--f2e', action='store_true', help='French to English translation')
        parser.add_argument('--direct', action='store_true', help='Enable direct translation tasks')
        parser.add_argument('--match', action='store_true', help='Enable matching tasks')
        parser.add_argument('--ignore-accents', action='store_true',
                          help='Treat accented and non-accented versions as identical')

    def __init__(self, args):
        self.direction = 'e2f' if args.e2f else 'f2e'
        self.current_vocab = self.E2F_VOCAB if args.e2f else self.F2E_VOCAB
        self.active_modes = []
        if args.direct: self.active_modes.append('direct')
        if args.match: self.active_modes.append('match')
        if not self.active_modes:
            self.active_modes = ['direct', 'match']
            
        self.ignore_accents = args.ignore_accents
        self.source_words = list(self.current_vocab.keys())

    def generate_task(self):
        task_type = random.choice(self.active_modes)
        source_word = random.choice(self.source_words)
        
        if task_type == 'direct':
            return self._create_direct_task(source_word)
        return self._create_match_task(source_word)

    def _create_direct_task(self, source_word):
        if self.direction == 'e2f':
            question = f"Translate to French: {source_word}"
        else:
            question = f"Translate to English: {source_word}"
            
        return question, self.current_vocab[source_word]

    def _create_match_task(self, source_word):
        correct_translations = self.current_vocab[source_word]
        correct = correct_translations[0]  # Use first translation as correct answer
        
        # Collect distractors from other words' translations
        distractors = []
        for word, translations in self.current_vocab.items():
            if word != source_word:
                distractors.extend(translations)
        
        options = random.sample(distractors, 2)  # Get 2 wrong answers
        options.append(correct)
        random.shuffle(options)
        
        correct_index = options.index(correct) + 1  # Options are 1-based
        
        question = f"Match translation for:\n{source_word}\n\nOptions:"
        for i, opt in enumerate(options, 1):
            question += f"\n{i}) {opt}"
            
        return question, correct_index

    def validate_answer(self, user_answer, correct):
        if isinstance(correct, list):  # Direct translation
            normalized_correct = [self._normalize(a) for a in correct]
            return self._normalize(user_answer) in normalized_correct
        
        # Matching task (correct is index)
        try:
            return int(user_answer) == correct
        except ValueError:
            return False

    def _normalize(self, text):
        normalized = unicodedata.normalize('NFKD', text.lower().strip())
        if self.ignore_accents:
            normalized = ''.join([c for c in normalized 
                                if not unicodedata.combining(c)])
        return normalized