import argparse
import importlib

from TimeoutException import TimeoutException
from QuizEngine import QuizEngine
from utils import safe_filename, clear_screen, check_filename_correctness


def create_parser(provider_class):
    """Create and configure argument parser with provider-specific arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True, help="Task provider, e.g.: `task_providers.math.MultiplicationTaskProvider`")
    parser.add_argument('--num-questions', type=int, default=10, help="How many questions in one session")
    parser.add_argument('--time-limit', type=float, help="Limit in seconds for each question")
    parser.add_argument('--clean-screen', action='store_true', help="Clear the terminal after each question")
    parser.add_argument('--no-summary', action='store_true', 
                      help="Ommit session summary at the end")
    parser.add_argument('--errors', choices=['hide', 'show', 'hint'], default='hint',
                      help='Control error message display (default: hint)')
    parser.add_argument('--mistakes', action='store_true', help='Include up to 3×num_questions previous mistakes')
    parser.add_argument('--file', help="File path to store results. Use '.json' or '.json.gz' extension.")
    provider_class.add_arguments(parser)
    return parser

def main():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--task', required=True)
    task_args, remaining = base_parser.parse_known_args()
    module_path, class_name = task_args.task.rsplit('.', 1)
    provider_class = getattr(importlib.import_module(module_path), class_name)

    parser = create_parser(provider_class)
    args = parser.parse_args()

    provider = provider_class(args)
    check_filename_correctness(args, provider)

    engine = QuizEngine(provider, args)
    engine.run()

if __name__ == '__main__':
    main()