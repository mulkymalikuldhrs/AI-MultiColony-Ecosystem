import os
from pathlib import Path

# Dapatkan direktori root proyek, dengan asumsi skrip ini ada di root
ROOT_DIR = Path(__file__).parent.resolve()
REPORTS_DIR = ROOT_DIR / "reports"
OUTPUT_FILE = REPORTS_DIR / "structure_current_branch.txt"
IGNORED_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    "node_modules",
    "build",
    "dist",
    "archive",
    ".continue",
    ".kilocode",
}


def main():
    # Pastikan direktori laporan ada
    REPORTS_DIR.mkdir(exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        f.write("File and Directory Structure Report\n")
        f.write("=" * 40 + "\n")

        for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
            # Abaikan direktori yang tidak diinginkan
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            # Hitung level untuk indentasi
            try:
                level = Path(root).relative_to(ROOT_DIR).parts
                level_count = len(level)
            except ValueError:
                level_count = 0

            indent = " " * 4 * level_count
            f.write(f"{indent}{os.path.basename(root)}/\n")

            subindent = " " * 4 * (level_count + 1)
            for file_name in files:
                f.write(f"{subindent}{file_name}\n")


if __name__ == "__main__":
    print(f"Generating report at: {OUTPUT_FILE}")
    main()
    print("Report generation complete.")
