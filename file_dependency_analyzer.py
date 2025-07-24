#!/usr/bin/env python3
"""
File Dependency Analyzer - Analisis konektivitas dan dependencies antar file
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class FileDependencyAnalyzer:
    """Analyzer untuk mengecek dependencies antar file"""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.file_dependencies = {}
        self.import_graph = {}
        self.file_usage = {}
        self.duplicate_files = {}
        self.launcher_files = []
        self.readme_files = []

    def analyze_all_files(self):
        """Analisis semua file dalam project"""
        print("🔍 Starting comprehensive file dependency analysis...")

        # 1. Scan semua file
        self._scan_all_files()

        # 2. Analisis imports dan dependencies
        self._analyze_imports()

        # 3. Cari file duplikat
        self._find_duplicate_files()

        # 4. Analisis launcher files
        self._analyze_launcher_files()

        # 5. Analisis README files
        self._analyze_readme_files()

        # 6. Cek file yang tidak digunakan
        self._find_unused_files()

        return self._generate_report()

    def _scan_all_files(self):
        """Scan semua file dalam project"""
        print("📁 Scanning all files...")

        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.root_path)

                # Kategorikan file
                if file_path.suffix == ".py":
                    self._analyze_python_file(file_path, relative_path)
                elif file_path.name.lower().startswith("readme"):
                    self.readme_files.append(str(relative_path))
                elif (
                    "launch" in file_path.name.lower()
                    or "main" in file_path.name.lower()
                ):
                    self.launcher_files.append(str(relative_path))

    def _analyze_python_file(self, file_path: Path, relative_path: Path):
        """Analisis file Python untuk imports dan dependencies"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST untuk mendapatkan imports
            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Cari references ke file lain
            file_references = self._find_file_references(content)

            self.file_dependencies[str(relative_path)] = {
                "imports": imports,
                "file_references": file_references,
                "size": file_path.stat().st_size,
                "lines": len(content.splitlines()),
            }

        except Exception as e:
            print(f"⚠️ Error analyzing {relative_path}: {e}")

    def _find_file_references(self, content: str) -> List[str]:
        """Cari referensi ke file lain dalam content"""
        references = []

        # Pattern untuk mencari referensi file
        patterns = [
            r'["\']([^"\']*\.py)["\']',  # "file.py"
            r'["\']([^"\']*\.yaml)["\']',  # "config.yaml"
            r'["\']([^"\']*\.json)["\']',  # "data.json"
            r'["\']([^"\']*\.md)["\']',  # "readme.md"
            r"from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import",  # from module import
            r"import\s+([a-zA-Z_][a-zA-Z0-9_.]*)",  # import module
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            references.extend(matches)

        return list(set(references))

    def _analyze_imports(self):
        """Analisis import graph"""
        print("🔗 Analyzing import dependencies...")

        for file_path, data in self.file_dependencies.items():
            self.import_graph[file_path] = []

            for import_name in data["imports"]:
                # Cari file yang sesuai dengan import
                matching_files = self._find_matching_files(import_name)
                self.import_graph[file_path].extend(matching_files)

    def _find_matching_files(self, import_name: str) -> List[str]:
        """Cari file yang sesuai dengan nama import"""
        matching_files = []

        # Convert import name ke path
        possible_paths = [
            f"{import_name.replace('.', '/')}.py",
            f"{import_name.replace('.', '/')}/__init__.py",
            f"colony/{import_name.replace('.', '/')}.py",
            f"colony/{import_name.replace('.', '/')}/__init__.py",
        ]

        for possible_path in possible_paths:
            if possible_path in self.file_dependencies:
                matching_files.append(possible_path)

        return matching_files

    def _find_duplicate_files(self):
        """Cari file yang mungkin duplikat berdasarkan nama dan konten"""
        print("🔍 Finding duplicate files...")

        file_groups = {}

        for file_path, data in self.file_dependencies.items():
            # Group berdasarkan nama file (tanpa path)
            filename = Path(file_path).name

            if filename not in file_groups:
                file_groups[filename] = []

            file_groups[filename].append(
                {"path": file_path, "size": data["size"], "lines": data["lines"]}
            )

        # Identifikasi potential duplicates
        for filename, files in file_groups.items():
            if len(files) > 1:
                self.duplicate_files[filename] = files

    def _analyze_launcher_files(self):
        """Analisis file launcher"""
        print("🚀 Analyzing launcher files...")

        launcher_analysis = {}

        for launcher_file in self.launcher_files:
            if launcher_file in self.file_dependencies:
                data = self.file_dependencies[launcher_file]
                launcher_analysis[launcher_file] = {
                    "size": data["size"],
                    "lines": data["lines"],
                    "imports": len(data["imports"]),
                    "references": len(data["file_references"]),
                }

        self.launcher_analysis = launcher_analysis

    def _analyze_readme_files(self):
        """Analisis file README"""
        print("📚 Analyzing README files...")

        readme_analysis = {}

        for readme_file in self.readme_files:
            file_path = self.root_path / readme_file
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    readme_analysis[readme_file] = {
                        "size": file_path.stat().st_size,
                        "lines": len(content.splitlines()),
                        "words": len(content.split()),
                        "has_toc": "table of contents" in content.lower()
                        or "toc" in content.lower(),
                        "has_badges": "![" in content or "badge" in content.lower(),
                        "has_installation": "install" in content.lower(),
                        "has_usage": "usage" in content.lower()
                        or "how to" in content.lower(),
                    }
                except Exception as e:
                    print(f"⚠️ Error reading {readme_file}: {e}")

        self.readme_analysis = readme_analysis

    def _find_unused_files(self):
        """Cari file yang tidak digunakan"""
        print("🗑️ Finding unused files...")

        used_files = set()

        # Mulai dari main entry points
        entry_points = ["main.py", "colony/api/app.py", "system_analyzer.py"]

        for entry_point in entry_points:
            if entry_point in self.file_dependencies:
                self._mark_file_as_used(entry_point, used_files)

        # File yang tidak digunakan
        all_files = set(self.file_dependencies.keys())
        self.unused_files = all_files - used_files

    def _mark_file_as_used(self, file_path: str, used_files: set, visited: set = None):
        """Mark file dan dependencies-nya sebagai used"""
        if visited is None:
            visited = set()

        if file_path in visited:
            return

        visited.add(file_path)
        used_files.add(file_path)

        # Mark dependencies
        if file_path in self.import_graph:
            for dependency in self.import_graph[file_path]:
                self._mark_file_as_used(dependency, used_files, visited)

    def _generate_report(self) -> Dict:
        """Generate comprehensive report"""
        print("📊 Generating analysis report...")

        report = {
            "summary": {
                "total_python_files": len(self.file_dependencies),
                "total_launcher_files": len(self.launcher_files),
                "total_readme_files": len(self.readme_files),
                "duplicate_file_groups": len(self.duplicate_files),
                "unused_files": (
                    len(self.unused_files) if hasattr(self, "unused_files") else 0
                ),
            },
            "launcher_files": (
                self.launcher_analysis if hasattr(self, "launcher_analysis") else {}
            ),
            "readme_files": (
                self.readme_analysis if hasattr(self, "readme_analysis") else {}
            ),
            "duplicate_files": self.duplicate_files,
            "unused_files": (
                list(self.unused_files) if hasattr(self, "unused_files") else []
            ),
            "file_dependencies": self.file_dependencies,
            "import_graph": self.import_graph,
        }

        return report

    def get_safe_to_delete_files(self) -> Dict[str, List[str]]:
        """Dapatkan daftar file yang aman untuk dihapus"""
        safe_to_delete = {
            "duplicate_readmes": [],
            "old_launchers": [],
            "backup_files": [],
            "unused_files": [],
        }

        # README files - keep only the main one
        if hasattr(self, "readme_analysis"):
            readme_files = list(self.readme_analysis.keys())
            if "README.md" in readme_files:
                # Keep README.md, mark others as safe to delete
                for readme in readme_files:
                    if readme != "README.md":
                        safe_to_delete["duplicate_readmes"].append(readme)
            elif readme_files:
                # Keep the largest/most comprehensive one
                best_readme = max(
                    readme_files, key=lambda x: self.readme_analysis[x]["lines"]
                )
                for readme in readme_files:
                    if readme != best_readme:
                        safe_to_delete["duplicate_readmes"].append(readme)

        # Launcher files - keep only main.py
        if hasattr(self, "launcher_analysis"):
            for launcher in self.launcher_analysis.keys():
                if launcher != "main.py" and "old" in launcher.lower():
                    safe_to_delete["old_launchers"].append(launcher)

        # Backup files
        for file_path in self.file_dependencies.keys():
            if any(
                pattern in file_path.lower()
                for pattern in ["_old", "_backup", "_bak", ".bak"]
            ):
                safe_to_delete["backup_files"].append(file_path)

        # Unused files (be very careful with this)
        if hasattr(self, "unused_files"):
            for unused_file in self.unused_files:
                # Only mark as safe if it's clearly a backup or test file
                if any(
                    pattern in unused_file.lower()
                    for pattern in ["test_", "_test", "example_", "_example"]
                ):
                    safe_to_delete["unused_files"].append(unused_file)

        return safe_to_delete

    def print_analysis_report(self):
        """Print human-readable analysis report"""
        print("\n" + "=" * 80)
        print("🔍 FILE DEPENDENCY ANALYSIS REPORT")
        print("=" * 80)

        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"├── Total Python files: {len(self.file_dependencies)}")
        print(f"├── Launcher files: {len(self.launcher_files)}")
        print(f"├── README files: {len(self.readme_files)}")
        print(f"├── Duplicate file groups: {len(self.duplicate_files)}")
        print(
            f"└── Unused files: {len(self.unused_files) if hasattr(self, 'unused_files') else 0}"
        )

        # Launcher files
        if hasattr(self, "launcher_analysis"):
            print(f"\n🚀 LAUNCHER FILES:")
            for launcher, data in self.launcher_analysis.items():
                print(f"├── {launcher}")
                print(f"│   ├── Size: {data['size']} bytes")
                print(f"│   ├── Lines: {data['lines']}")
                print(f"│   └── Imports: {data['imports']}")

        # README files
        if hasattr(self, "readme_analysis"):
            print(f"\n📚 README FILES:")
            for readme, data in self.readme_analysis.items():
                print(f"├── {readme}")
                print(f"│   ├── Size: {data['size']} bytes")
                print(f"│   ├── Lines: {data['lines']}")
                print(f"│   ├── Words: {data['words']}")
                print(
                    f"│   └── Features: {', '.join([k for k, v in data.items() if isinstance(v, bool) and v])}"
                )

        # Duplicate files
        if self.duplicate_files:
            print(f"\n🔍 DUPLICATE FILES:")
            for filename, files in self.duplicate_files.items():
                if len(files) > 1:
                    print(f"├── {filename} ({len(files)} copies):")
                    for file_info in files:
                        print(
                            f"│   ├── {file_info['path']} ({file_info['lines']} lines)"
                        )

        # Safe to delete
        safe_to_delete = self.get_safe_to_delete_files()
        print(f"\n🗑️ SAFE TO DELETE:")
        for category, files in safe_to_delete.items():
            if files:
                print(f"├── {category.replace('_', ' ').title()}:")
                for file in files:
                    print(f"│   └── {file}")

        print("\n" + "=" * 80)


def main():
    """Main function"""
    analyzer = FileDependencyAnalyzer()

    # Run analysis
    report = analyzer.analyze_all_files()

    # Print report
    analyzer.print_analysis_report()

    # Save detailed report
    with open("file_dependency_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Detailed report saved to: file_dependency_report.json")

    return analyzer


if __name__ == "__main__":
    main()
