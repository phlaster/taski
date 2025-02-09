import argparse
import importlib
import json
import gzip
import os
import random
import re
import sys
import time
from datetime import datetime
from queue import Queue
from statistics import median
from threading import Thread

class TimeoutException(Exception): pass

def safe_filename(name):
    """Convert quiz name to filesystem-safe name"""
    return re.sub(r'[^\w-]', '_', name).strip('_')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_filename_correctness(args, provider):
    if not args.file:
        unzipped_name = os.path.join('results', f"{safe_filename(provider.name)}.json")
        zipped_name = unzipped_name + ".gz"

        if os.path.exists(unzipped_name) and os.path.exists(zipped_name):
            print("Automatic naming failed, 2 files with appropriate names were found. State `--file` argument explicitly.")
            sys.exit(1)
        
        args.file = unzipped_name if os.path.exists(unzipped_name) else zipped_name

    if args.file:
        if not args.file.endswith(('.json', '.json.gz')):
            print("Error: Output file must have a '.json' or '.json.gz' extension.")
            sys.exit(1)

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
                
                # Collect most recent 3*num_questions questions
                recent_questions = []
                for session in reversed(data['sessions']):  # Newest sessions first
                    for q in reversed(session['questions']):  # Preserve original question order
                        recent_questions.insert(0, q)  # Add to beginning to maintain chronology
                        if len(recent_questions) >= 3 * self.args.num_questions:
                            break
                    if len(recent_questions) >= 3 * self.args.num_questions:
                        break
                
                # Extract mistakes from recent questions
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

            # Run the quiz loop
            self.retry_questions = self._load_retry_questions()[:self.args.num_questions]
            remaining_questions = self.args.num_questions - len(self.retry_questions)

            # Run the quiz loop
            for _ in range(self.args.num_questions):
                try:
                    task = self._get_next_task()
                    self._ask_question(*task)
                    if self.args.clean_screen:
                        clear_screen()
                except KeyboardInterrupt:
                    print("\nQuiz interrupted by the user.")
                    break  # Exit the question loop
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
            # Wait for user to press Enter
            input("Press Enter to continue...")
        # Clear screen after handling feedback
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

    def print_session_summary(self):
        print(f"\nSession Summary:")
        print(f"\tQuestions: {self.session_data['statistics']['correct_answers']}/{self.session_data['statistics']['total_questions']}")
        print(f"\tSession accuracy: {self.session_data['statistics']['accuracy']}%")
        print(f"\tAverage time per question: {self.session_data['statistics']['average_time']}s")
        print(f"\tFastest correct answer: {self.session_data['statistics']['fastest_correct'] or 'N/A'}s")
        print(f"\tSlowest answer: {self.session_data['statistics']['slowest_answer']}s")
        print(f"\tTotal time: {self.session_data['duration']}s")
        print(f"\tFilename: {self.args.file}")

    def _finalize_session(self):
        if not self.session_data['questions']:  # No questions were answered
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
            'average_time': round(sum(times)/len(times), 2) if times else 0,
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
        
        if not self.args.no_summary: self.print_session_summary()


def main():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--task', required=True)
    task_args, remaining = base_parser.parse_known_args()
    module_path, class_name = task_args.task.rsplit('.', 1)
    provider_class = getattr(importlib.import_module(module_path), class_name)

    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--num-questions', type=int, default=10)
    parser.add_argument('--time-limit', type=float)
    parser.add_argument('--clean-screen', action='store_true')
    parser.add_argument('--no-summary', action='store_true', help="Do not print session summary upon the exit")
    parser.add_argument('--errors', choices=['hide', 'show', 'hint'], default='hint', help='Control error message display (default: hint)')
    parser.add_argument('--mistakes', action='store_true', help='Include up to 3×num_questions previous mistakes')
    parser.add_argument('--file', help="File path to store the results in. Use '.json' for uncompressed or '.json.gz' for compressed.")
    provider_class.add_arguments(parser)
    args = parser.parse_args()

    provider = provider_class(args)
    check_filename_correctness(args, provider)

    engine = QuizEngine(provider, args)
    engine.run()

if __name__ == '__main__':
    main()