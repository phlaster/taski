import argparse
import importlib
import json
import os
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
        self.session_data = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'questions': [],
            'statistics': {},
            'settings': vars(args)
        }

    def run(self):

        print(f"\n{self.task_provider.description}\n")
        input("Press Enter to start the quiz...")
        
        if self.args.clean_screen:
            clear_screen()
            
        self.session_data['start_time'] = datetime.now().isoformat()
        
        try:
            for _ in range(self.args.num_questions):
                self._ask_question()
                if self.args.clean_screen:
                    clear_screen()
        finally:
            self._finalize_session()

    def _ask_question(self):
        question, correct = self.task_provider.generate_task()
        print(f"\nQ{len(self.session_data['questions'])+1}: {question}")
        
        start = time.time()
        try:
            answer = input_with_timeout("Answer: ", self.args.time_limit)
        except TimeoutException:
            answer = None
            print("\nTime's up!")
        elapsed = time.time() - start

        is_correct = self._validate_answer(answer, correct)
        self._store_result(question, correct, answer, elapsed, is_correct)
        print("Correct!" if is_correct else f"Wrong. Correct answer: {correct}")

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

    def _finalize_session(self):
        self.session_data['end_time'] = datetime.now().isoformat()
        self.session_data['duration'] = round(
            (datetime.fromisoformat(self.session_data['end_time']) - 
             datetime.fromisoformat(self.session_data['start_time'])).total_seconds(), 2)
        
        # Calculate statistics
        times = [q['time_taken'] for q in self.session_data['questions']]
        correct_times = [q['time_taken'] for q in self.session_data['questions'] if q['is_correct']]
        
        self.session_data['statistics'] = {
            'average_time': round(sum(times)/len(times), 2) if times else 0,
            'median_time': round(median(times), 2) if times else 0,
            'fastest_correct': round(min(correct_times), 2) if correct_times else None,
            'slowest_answer': round(max(times), 2) if times else 0
        }
        
        # Prepare output structure
        output_data = {
            'quiz_name': self.task_provider.name,
            'sessions': []
        }
        
        # Load existing data if file exists
        output_path = self.args.output
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                existing_data = json.load(f)
                if existing_data['quiz_name'] != output_data['quiz_name']:
                    raise ValueError(f"Existing file contains different quiz type: {existing_data['quiz_name']}")
                output_data['sessions'] = existing_data['sessions']

        # Add new session
        output_data['sessions'].append(self.session_data)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write updated data
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nSession saved to {output_path}")

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
    parser.add_argument('--output')
    provider_class.add_arguments(parser)
    args = parser.parse_args()

    provider = provider_class(args)
    
    # Set default output path if not specified
    if not args.output:
        filename = f"{safe_filename(provider.name)}.json"
        args.output = os.path.join('results', filename)

    engine = QuizEngine(provider, args)
    engine.run()

if __name__ == '__main__':
    main()