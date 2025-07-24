import json
import os
import subprocess
from pathlib import Path

# --- Konfigurasi ---
ROOT_DIR = Path(__file__).parent.resolve()
OUTPUT_FILE = "system_analysis_report.json"
IGNORED_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    "node_modules",
    "build",
    "dist",
    "archive",
}
FILE_EXTENSIONS_TO_LINT = {".py"}
FRONTEND_DIR = ROOT_DIR / "web-interface" / "react-ui"

# --- Fungsi Bantuan ---


def run_command(command, cwd="."):
    """Menjalankan perintah shell dan mengembalikan output."""
    try:
        result = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=True, shell=True
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip()


def get_dir_size(path):
    """Menghitung ukuran direktori."""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_dir_size(entry.path)
    return total


# --- Fase Analisis ---


def analyze_directory_structure():
    """Menganalisis dan melaporkan struktur direktori."""
    report = {"files": [], "folders": [], "suspicious_files": []}
    suspicious_patterns = [".swp", ".copy.py", ".pyc", ".log", "temp_"]

    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for name in files:
            file_path = Path(root) / name
            report["files"].append(str(file_path.relative_to(ROOT_DIR)))
            if any(pattern in name for pattern in suspicious_patterns):
                report["suspicious_files"].append(str(file_path.relative_to(ROOT_DIR)))

        for name in dirs:
            dir_path = Path(root) / name
            report["folders"].append(str(dir_path.relative_to(ROOT_DIR)))

    return report


def lint_python_files():
    """Menjalankan ruff untuk memeriksa file Python."""
    report = {"errors": [], "summary": ""}

    # Coba instal ruff jika belum ada
    try:
        import ruff
    except ImportError:
        print("Ruff not found, installing...")
        run_command("pip install ruff")

    command = f"ruff check {ROOT_DIR} --output-format=json"
    stdout, stderr = run_command(command)

    if stdout:
        try:
            report["errors"] = json.loads(stdout)
            report["summary"] = f"Found {len(report['errors'])} issues."
        except json.JSONDecodeError:
            report["summary"] = "Error parsing ruff output."
            report["errors"] = [stdout]

    if stderr:
        report["summary"] += f" Stderr: {stderr}"

    return report


def check_dependencies():
    """Memeriksa file dependensi."""
    report = {"requirements": {}, "package_json": {}}

    # Periksa requirements.txt
    req_file = ROOT_DIR / "requirements.txt"
    if req_file.exists():
        with open(req_file, "r") as f:
            report["requirements"]["prod"] = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith("#")
            ]

    dev_req_file = ROOT_DIR / "requirements-dev.txt"
    if dev_req_file.exists():
        with open(dev_req_file, "r") as f:
            report["requirements"]["dev"] = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith("#")
            ]

    # Periksa package.json
    pkg_json_file = FRONTEND_DIR / "package.json"
    if pkg_json_file.exists():
        with open(pkg_json_file, "r") as f:
            data = json.load(f)
            report["package_json"]["dependencies"] = list(
                data.get("dependencies", {}).keys()
            )
            report["package_json"]["devDependencies"] = list(
                data.get("devDependencies", {}).keys()
            )

    return report


def check_frontend():
    """Menjalankan pemeriksaan pada frontend."""
    report = {"lint_output": "", "pages_found": []}

    if not FRONTEND_DIR.exists():
        report["lint_output"] = "Frontend directory not found."
        return report

    # Jalankan npm install jika node_modules tidak ada
    if not (FRONTEND_DIR / "node_modules").exists():
        print("Running npm install in frontend directory...")
        run_command("npm install", cwd=str(FRONTEND_DIR))

    # Jalankan lint
    print("Running npm run lint in frontend directory...")
    stdout, stderr = run_command("npm run lint", cwd=str(FRONTEND_DIR))
    report["lint_output"] = {"stdout": stdout, "stderr": stderr}

    # Periksa halaman
    pages_dir = FRONTEND_DIR / "src" / "pages"
    if pages_dir.exists():
        report["pages_found"] = [f.name for f in pages_dir.iterdir() if f.is_file()]

    return report


def test_agent_registry():
    """Menjalankan tes minimal pada agent registry."""
    report = {"status": "FAIL", "error": "", "agents_list": []}
    try:
        # Menambahkan path colony ke sys.path
        import sys

        sys.path.append(str(ROOT_DIR))

        from colony.core.agent_registry import REGISTRY, list_all_agents

        agents = list_all_agents()
        report["agents_list"] = agents
        report["status"] = "SUCCESS"
        report["error"] = ""

    except ImportError as e:
        report["error"] = f"ImportError: {e}"
    except Exception as e:
        report["error"] = f"Exception: {e}"

    return report


# --- Main Execution ---


def main():
    """Fungsi utama untuk menjalankan semua analisis."""
    full_report = {}

    print("1. Menganalisis struktur direktori...")
    full_report["directory_structure"] = analyze_directory_structure()

    print("2. Menjalankan linter Python (ruff)...")
    full_report["python_linting"] = lint_python_files()

    print("3. Memeriksa file dependensi...")
    full_report["dependencies"] = check_dependencies()

    print("4. Memeriksa frontend...")
    full_report["frontend"] = check_frontend()

    print("5. Menjalankan tes minimal registry agen...")
    full_report["agent_registry_test"] = test_agent_registry()

    # Menulis laporan ke file JSON
    with open(OUTPUT_FILE, "w") as f:
        json.dump(full_report, f, indent=2)

    print(f"\nAnalisis selesai. Laporan lengkap disimpan di {OUTPUT_FILE}")

    # Mencetak ringkasan
    print("\n--- Ringkasan Analisis ---")
    print(f"Total file: {len(full_report['directory_structure']['files'])}")
    print(f"Total folder: {len(full_report['directory_structure']['folders'])}")
    print(
        f"File mencurigakan: {len(full_report['directory_structure']['suspicious_files'])}"
    )
    print(f"Masalah Python (ruff): {len(full_report['python_linting']['errors'])}")
    print(
        f"Dependensi Produksi Python: {len(full_report['dependencies']['requirements'].get('prod', []))}"
    )
    print(f"Status Tes Registry Agen: {full_report['agent_registry_test']['status']}")
    if full_report["agent_registry_test"]["status"] == "FAIL":
        print(f"  Error: {full_report['agent_registry_test']['error']}")
    print("--------------------------")


if __name__ == "__main__":
    main()
