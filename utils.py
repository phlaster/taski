import os
import sys
import re


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
            print(f"""Automatic naming failed, multiple files with appropriate names were found:
                > {unzipped_name}
                > {zipped_name}\nProvide explicit `--file` argument.""")
            sys.exit(1)
        
        args.file = unzipped_name if os.path.exists(unzipped_name) else zipped_name

    if args.file:
        if not args.file.endswith(('.json', '.json.gz')):
            print("Error: Output file must have a '.json' or '.json.gz' extension.")
            sys.exit(1)