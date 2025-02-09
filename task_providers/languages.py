import random
import unicodedata
import csv
import os
from .base import TaskProvider

class FrenchWordsTaskProvider(TaskProvider):
    def parse_csv_to_dict(self, file_path):
        result = {}        
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    key = row[0].strip()
                    values = [value.strip() for value in row[1:] if value.strip()]
                    result[key] = values
        return result

    @property
    def name(self):
        return "French Vocabulary Practice"

    @property
    def description(self):
        direction = "English to French" if self.direction == "e2f" else "French to English"
        return f"""French Vocabulary Practice ({direction})
        
        Task types enabled: {", ".join(self.active_modes)}
        Accent handling: {"Ignored" if self.ignore_accents else "Strict"}
        Total words in vocabulary: {len(self.current_vocab)}
        Press Enter to begin when ready."""

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("--e2f", action="store_true", default=False, help="English to French translation")
        parser.add_argument("--f2e", action="store_true", default=False, help="French to English translation")
        parser.add_argument("--direct", action="store_true", help="Enable direct translation tasks")
        parser.add_argument("--match", action="store_true", help="Enable matching tasks")
        parser.add_argument("--ignore-accents", action="store_true",
                          help="Treat accented and non-accented versions as identical")
        parser.add_argument("--match-options", type=int, default=3, help="How many options are in match tasks")


    def __init__(self, args):
        self.E2F_VOCAB = self.parse_csv_to_dict(os.path.join("task_providers", "e2f.csv"))
        self.F2E_VOCAB = self.parse_csv_to_dict(os.path.join("task_providers", "f2e.csv"))
        self.direction = "both" if (args.e2f == args.f2e) else "e2f" if args.e2f else "f2e"
        match self.direction:
            case "e2f":  
                self.current_vocab = self.E2F_VOCAB
            case "f2e":  
                self.current_vocab = self.F2E_VOCAB
            case "both":
                unique_keys = set(self.E2F_VOCAB.keys()).symmetric_difference(set(self.F2E_VOCAB.keys()))
                self.current_vocab = {k: self.E2F_VOCAB.get(k, self.F2E_VOCAB.get(k)) for k in unique_keys}
        
        self.active_modes = []
        if args.direct: self.active_modes.append("direct")
        if args.match: self.active_modes.append("match")
        if not self.active_modes:
            self.active_modes = ["direct", "match"]
        
        self.match_options = args.match_options
        self.ignore_accents = args.ignore_accents
        self.source_words = list(self.current_vocab.keys())

    def generate_task(self):
        task_type = random.choice(self.active_modes)
        source_word = random.choice(self.source_words)
        
        if task_type == "direct":
            return self._create_direct_task(source_word)
        return self._create_match_task(source_word)

    def _create_direct_task(self, source_word):
        if self.direction == "e2f":
            question = f"Translate to French: {source_word}"
        elif self.direction == "f2e":
            question = f"Translate to English: {source_word}"
        elif source_word in self.E2F_VOCAB:
            question = f"Translate to French: {source_word}"
        else:
            question = f"Translate to English: {source_word}"

        return question, self.current_vocab[source_word]

    def _create_match_task(self, source_word):
        source_lang = "English" if source_word in self.E2F_VOCAB else "French"
        target_lang = "French" if source_lang == "English" else "English"
        vocab = self.E2F_VOCAB if source_lang=="English" else self.F2E_VOCAB
        correct_translations = vocab[source_word]
        correct = random.choice(correct_translations)
        
        distractors = []
        for word, translations in vocab.items():
            if word != source_word:
                distractors.extend(translations)
        
        options = random.sample(distractors, min(max(self.match_options - 1, 2), len(distractors)))
        options.append(correct)
        random.shuffle(options)
        
        correct_index = options.index(correct) + 1
        
        question = f"Match {target_lang} translation for:\n{source_word}\n"
        for i, opt in enumerate(options, 1):
            question += f"\n{i}) {opt}"
            
        return question, correct_index

    def validate_answer(self, user_answer, correct):
        if isinstance(correct, list):
            normalized_correct = [self._normalize(a) for a in correct]
            return self._normalize(user_answer) in normalized_correct
        try:
            return int(user_answer) == correct
        except ValueError:
            return False

    def _normalize(self, text):
        normalized = unicodedata.normalize("NFKD", text.lower().strip())
        if self.ignore_accents:
            normalized = "".join([c for c in normalized 
                                if not unicodedata.combining(c)])
        return normalized