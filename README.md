# Taski - Command-Line Quiz Application

A modular quiz system with multiple question providers and progress tracking.

## Features

- Multiple quiz types (math, language learning)
- Time-limited questions
- Mistake tracking and retry system
- Session statistics and history
- Cross-platform compatibility

## Installation

1. Clone repository:
    ```bash
    git clone https://github.com/phlaster/taski
    cd taski
    ```

2. Create virtual environment (recommended):
    No external packages required now, but this may change in future
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate  # Windows
    ```

## Usage

### Basic Command
```bash
python main.py --task <TASK_PROVIDER> [--help] [OPTIONS]
```

### Core Arguments
| Argument               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `--task TASK`          | **Required** Question provider (e.g. `task_providers.math.MathTaskProvider`)|
| `--help`               | Prints all command line option for given provider and exits                 |
| `--num-questions N`    | Number of questions (default: 10)                                           |
| `--time-limit SECONDS` | Answer time limit per question                                              |
| `--clean-screen`       | Clear screen between questions                                              |
| `--errors MODE`        | Feedback mode: `hide`, `show`, or `hint` (default)                          |
| `--mistakes`           | Include previous mistakes (3×num_questions window)                          |
| `--file PATH`          | Custom results file path (default: auto-generated in `results/`)            |
| `--no-summary`         | Disable end-of-session statistics                                           |

## Task Providers

### 1. Math Practice
```bash
python main.py --task task_providers.math.MathTaskProvider
```
**Options:**
- `--max-factor N` - Maximum multiplicand value (default: 12)
- `--sum-factor N` - Summation tasks up to 10^? (default: 2)

### 2. French Vocabulary
```bash
python main.py --task task_providers.languages.FrenchWordsTaskProvider
```
**Options:**
- `--e2f`          - Enable English→French translation
- `--f2e`          - Enable French→English translation  
- `--direct`       - Enable direct translation tasks
- `--match`        - Enable multiple-choice tasks
- `--ignore-accents` - Treat accented/non-accented as identical
- `--match-options N` - Options in match tasks (default: 3)

## Examples

1. Basic Math quiz:
    ```bash
    python main.py --task task_providers.math.MathTaskProvider --num-questions 15
    ```

2. French practice with mistake retries:
    ```bash
    python main.py --task task_providers.languages.FrenchWordsTaskProvider \
    --num-questions 10 \
    --mistakes \
    --errors show
    ```

3. Timed quiz with clean interface:
    ```bash
    python main.py --task task_providers.math.MathTaskProvider \
    --time-limit 5 \
    --clean-screen \
    --errors hide
    ```

## Result Storage

- Results saved in JSON format (optionally gzipped)
- Automatic filename generation based on quiz type
- File locations:
  - `results/<quiz_name>.json`
  - `results/<quiz_name>.json.gz`

## Session Summary

End-of-session report includes:
- Total time elapsed
- Questions answered correctly
- Average/median answer times
- Fastest correct answer
- Slowest answer
- Session accuracy percentage

## Notes

- Mistake tracking uses sliding window of last 3×num_questions answers
- Corrected mistakes stop appearing once they exit the recent answer window
- Answer validation handles:
  - Numeric answers for math tasks
  - Accent variations for language tasks (when enabled)
  - Multiple correct answers (e.g. synonym translations)
