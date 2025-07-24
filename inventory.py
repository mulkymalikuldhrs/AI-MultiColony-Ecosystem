import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
OUTPUT_FILE = ROOT_DIR / "reports" / "structure_current_branch.txt"
IGNORED_DIRS = {"__pycache__", ".git", ".idea", "node_modules", "build", "dist", "archive", ".continue", ".kilocode"}

def main():
    with open(OUTPUT_FILE, "w") as f:
        for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            level = root.replace(str(ROOT_DIR), '').count(os.sep)
            indent = ' ' * 4 * (level)
            f.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                f.write(f'{subindent}{file}\n')

if __name__ == "__main__":
    main()
