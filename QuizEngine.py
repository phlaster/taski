import json
import gzip
import os
import sys
import random
import time
from queue import Queue
from threading import Thread

from datetime import datetime
from statistics import median, mean

from TimeoutException import TimeoutException
from utils import safe_filename, clear_screen

def input_with_timeout(prompt, timeout):
    print(prompt, end='', flush=True)
    q = Queue()
    t = Thread(target=lambda: q.put(sys.stdin.readline().strip()))
    t.daemon = True
    t.start()
    try:
        return q.get(timeout=timeout)
    except Exception:
        raise TimeoutException()
    finally:
        t.join(0)


class QuizEngine:
    def __init__(self, task_provider, args):
        self.task_provider = task_provider
        self.args = args
        self.retry_questions = []
        self.session_data = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'questions': [],
            'statistics': {},
            'settings': vars(args)
        }
    def _load_retry_questions(self):
        """Load previous incorrect answers from result files"""
        safe_name = safe_filename(self.task_provider.name)
        file_candidates = [
            os.path.join('results', f"{safe_name}.json"),
            os.path.join('results', f"{safe_name}.json.gz")
        ]
        existing_files = [f for f in file_candidates if os.path.exists(f)]
        
        if not existing_files:
            return []
        
        try:
            file_path = existing_files[0]
            open_func = gzip.open if file_path.endswith('.gz') else open
            mode = 'rt' if file_path.endswith('.gz') else 'r'
            
            with open_func(file_path, mode) as f:
                data = json.load(f)
                if data['quiz_name'] != self.task_provider.name:
                    return []
                
                recent_questions = []
                for session in reversed(data['sessions']):
                    for q in reversed(session['questions']):
                        recent_questions.insert(0, q)
                        if len(recent_questions) >= 3 * self.args.num_questions:
                            break
                    if len(recent_questions) >= 3 * self.args.num_questions:
                        break
                
                errors = [q for q in recent_questions if not q['is_correct']]
                random.shuffle(errors)
                return [(q['question'], q['correct_answer']) for q in errors[:self.args.num_questions]]
        except Exception as e:
            return []

    def run(self):
        try:
            print(f"\n{self.task_provider.description}\n")
            input("Press Enter to start the quiz...")
            if self.args.clean_screen:
                clear_screen()
            self.session_data['start_time'] = datetime.now().isoformat()

            self.retry_questions = self._load_retry_questions()[:self.args.num_questions]
            remaining_questions = self.args.num_questions - len(self.retry_questions)

            for _ in range(self.args.num_questions):
                try:
                    task = self._get_next_task()
                    self._ask_question(*task)
                    if self.args.clean_screen:
                        clear_screen()
                except KeyboardInterrupt:
                    print("\nQuiz interrupted by the user.")
                    break
        except KeyboardInterrupt:
            print("\nQuiz session terminated by the user before starting.")
        finally:
            self._finalize_session()

    def _get_next_task(self):
        if self.retry_questions:
            return self.retry_questions.pop(0)
        return self.task_provider.generate_task()

    def _ask_question(self, question, correct):
        """Ask a question, handling both new and retry questions"""
        is_retry = len(self.session_data['questions']) < self.args.mistakes
        print(f"\nQ{len(self.session_data['questions'])+1}: {question}")
        start = time.time()
        try:
            answer = input_with_timeout("Answer: ", self.args.time_limit)
        except TimeoutException:
            answer = None
            print("\nTime's up!")
        elapsed = time.time() - start
        is_correct = False if is_retry and not answer else self._validate_answer(answer, correct)
        self._store_result(question, correct, answer, elapsed, is_correct)
        if self.args.errors != 'hide':
            if is_correct:
                print("\033[32mCorrect!\033[0m")
            else:
                if self.args.errors == 'show':
                    print("\033[31mIncorrect!\033[0m")
                else:
                    if isinstance(correct, list):
                        correct_display = ', '.join(map(str, correct))
                    else:
                        correct_display = str(correct)
                    print(f"\033[31mIncorrect! Correct answer: {correct_display}\033[0m")
            input("Press Enter to continue...")
        if self.args.clean_screen:
            clear_screen()

    def _validate_answer(self, answer, correct):
        return answer is not None and \
            self.task_provider.validate_answer(answer, correct)

    def _store_result(self, question, correct, answer, time_taken, is_correct):
        self.session_data['questions'].append({
            'question': question,
            'correct_answer': correct,
            'user_answer': answer,
            'time_taken': round(time_taken, 2),
            'is_correct': is_correct
        })

    def _print_session_summary(self):
        print(f"\nSession Summary:")
        print(f"\tQuestions: {self.session_data['statistics']['correct_answers']}/{self.session_data['statistics']['total_questions']}")
        print(f"\tSession accuracy: {self.session_data['statistics']['accuracy']}%")
        print(f"\tAverage time per question: {self.session_data['statistics']['average_time']}s")
        print(f"\tFastest correct answer: {self.session_data['statistics']['fastest_correct'] or 'N/A'}s")
        print(f"\tSlowest answer: {self.session_data['statistics']['slowest_answer']}s")
        print(f"\tTotal time: {self.session_data['duration']}s")
        print(f"\tFilename: {self.args.file}")

    def _finalize_session(self):
        if not self.session_data['questions']:
            print("No questions were completed. Exiting without saving.")
            return

        self.session_data['end_time'] = datetime.now().isoformat()
        self.session_data['duration'] = round(
            (datetime.fromisoformat(self.session_data['end_time']) - 
             datetime.fromisoformat(self.session_data['start_time'])).total_seconds(), 2)
        times = [q['time_taken'] for q in self.session_data['questions']]
        total_questions = len(self.session_data['questions'])
        correct_answers = sum(q['is_correct'] for q in self.session_data['questions'])
        accuracy = round((correct_answers / total_questions * 100), 2) if total_questions > 0 else 0
        correct_times = [q['time_taken'] for q in self.session_data['questions'] if q['is_correct']]
        self.session_data['statistics'] = {
            'average_time': round(mean(times), 2) if times else 0,
            'median_time': round(median(times), 2) if times else 0,
            'fastest_correct': round(min(correct_times), 2) if correct_times else None,
            'slowest_answer': round(max(times), 2) if times else 0,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': accuracy
        }

        output_data = {
            'quiz_name': self.task_provider.name,
            'sessions': []
        }
        if self.args.file.endswith('.json.gz'):
            mode = 'gzip'
        elif self.args.file.endswith('.json'):
            mode = 'json'
        else:
            print("Error: Output file must have a '.json' or '.json.gz' extension.")
            sys.exit(1)
        output_path = self.args.file
        if os.path.exists(output_path):
            if mode == 'gzip':
                with gzip.open(output_path, 'rt') as f:
                    existing_data = json.load(f)
            else:
                with open(output_path, 'r') as f:
                    existing_data = json.load(f)
            if existing_data['quiz_name'] != self.task_provider.name:
                raise ValueError(f"Existing file contains different quiz type: {existing_data['quiz_name']}")
            output_data['sessions'] = existing_data['sessions']
        output_data['sessions'].append(self.session_data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if mode == 'gzip':
            with gzip.open(output_path, 'wt') as f:
                json.dump(output_data, f, indent=2)
        else:
             with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)
        
        if not self.args.no_summary: self._print_session_summary()