#!/usr/bin/env python3
"""
Safe File Cleanup - Menghapus file duplikat dan tidak diperlukan dengan aman
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
import json

class SafeFileCleanup:
    """Safe file cleanup utility"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / "cleanup_backup"
        self.deleted_files = []
        
    def create_backup_dir(self):
        """Buat direktori backup"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            print(f"📁 Created backup directory: {self.backup_dir}")
    
    def backup_file(self, file_path: str):
        """Backup file sebelum dihapus"""
        source = self.root_path / file_path
        if source.exists():
            # Buat struktur direktori di backup
            backup_path = self.backup_dir / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, backup_path)
            print(f"💾 Backed up: {file_path}")
            return True
        return False
    
    def safe_delete_file(self, file_path: str, reason: str = ""):
        """Hapus file dengan aman (backup dulu)"""
        if self.backup_file(file_path):
            source = self.root_path / file_path
            source.unlink()
            self.deleted_files.append({
                'file': file_path,
                'reason': reason,
                'backup_location': str(self.backup_dir / file_path)
            })
            print(f"🗑️ Deleted: {file_path} ({reason})")
            return True
        return False
    
    def cleanup_duplicate_readmes(self):
        """Cleanup README files duplikat"""
        print("\n📚 Cleaning up duplicate README files...")
        
        # Keep only README.md, delete others
        readme_files_to_delete = [
            "README_OLD.md",
            "README_UNIFIED.md", 
            "docs/README_COMPREHENSIVE.md",
            "docs/README_RELEASE.md"
        ]
        
        for readme_file in readme_files_to_delete:
            if (self.root_path / readme_file).exists():
                self.safe_delete_file(readme_file, "Duplicate README - keeping main README.md")
    
    def cleanup_duplicate_launchers(self):
        """Cleanup launcher files duplikat"""
        print("\n🚀 Cleaning up duplicate launcher files...")
        
        # Keep main.py, check for other launchers
        launcher_files_to_check = [
            "unified_launcher.py",  # Root level - might be old
            "colony/core/unified_launcher.py"  # Core level - might be newer
        ]
        
        # Cek mana yang digunakan oleh main.py
        main_py_content = ""
        if (self.root_path / "main.py").exists():
            with open(self.root_path / "main.py", 'r') as f:
                main_py_content = f.read()
        
        # Jika main.py tidak menggunakan unified_launcher, hapus keduanya
        if "unified_launcher" not in main_py_content:
            for launcher in launcher_files_to_check:
                if (self.root_path / launcher).exists():
                    self.safe_delete_file(launcher, "Unused launcher - main.py is the unified entry point")
    
    def cleanup_duplicate_registries(self):
        """Cleanup agent registry duplikat"""
        print("\n🤖 Analyzing agent registry files...")
        
        # Kedua registry digunakan, jadi kita perlu merge atau pilih satu
        core_registry = self.root_path / "colony/core/agent_registry.py"
        agents_registry = self.root_path / "colony/agents/agent_registry.py"
        
        if core_registry.exists() and agents_registry.exists():
            print("⚠️ Found two agent registries - both are used by main.py")
            print("   Keeping both for now - manual merge may be needed")
            # Tidak hapus karena keduanya digunakan
    
    def cleanup_duplicate_credential_managers(self):
        """Cleanup credential manager duplikat"""
        print("\n🔐 Analyzing credential manager files...")
        
        core_cred = self.root_path / "colony/core/credential_manager.py"
        agents_cred = self.root_path / "colony/agents/credential_manager.py"
        
        if core_cred.exists() and agents_cred.exists():
            # Cek mana yang lebih lengkap
            core_size = core_cred.stat().st_size
            agents_size = agents_cred.stat().st_size
            
            print(f"   Core credential_manager: {core_size} bytes")
            print(f"   Agents credential_manager: {agents_size} bytes")
            
            # Keep yang lebih besar (lebih lengkap), tapi backup yang kecil
            if agents_size > core_size:
                self.safe_delete_file("colony/core/credential_manager.py", 
                                    "Smaller credential manager - keeping agents version")
            else:
                self.safe_delete_file("colony/agents/credential_manager.py",
                                    "Smaller credential manager - keeping core version")
    
    def cleanup_backup_files(self):
        """Cleanup file backup dan temporary"""
        print("\n🧹 Cleaning up backup and temporary files...")
        
        backup_patterns = [
            "*_old.*",
            "*_backup.*", 
            "*_bak.*",
            "*.bak",
            "*~",
            "*.tmp",
            "__pycache__",
            "*.pyc"
        ]
        
        for pattern in backup_patterns:
            for file_path in self.root_path.rglob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.root_path)
                    self.safe_delete_file(str(relative_path), f"Backup/temporary file ({pattern})")
                elif file_path.is_dir() and pattern == "__pycache__":
                    # Hapus direktori __pycache__
                    shutil.rmtree(file_path)
                    print(f"🗑️ Deleted directory: {file_path.relative_to(self.root_path)}")
    
    def cleanup_copy_files(self):
        """Cleanup file dengan nama 'copy'"""
        print("\n📄 Cleaning up copy files...")
        
        copy_files = [
            "colony/core/__init__ copy.py",
            "colony/agents/__init__ copy.py"
        ]
        
        for copy_file in copy_files:
            if (self.root_path / copy_file).exists():
                self.safe_delete_file(copy_file, "Copy file - not needed")
    
    def cleanup_test_files(self):
        """Cleanup file test yang tidak digunakan"""
        print("\n🧪 Cleaning up unused test files...")
        
        # Hanya hapus test files yang jelas tidak digunakan
        test_files_to_delete = [
            "test_ecosystem.py",
            "test_simple_daemon.py", 
            "test_daemon.py"
        ]
        
        for test_file in test_files_to_delete:
            if (self.root_path / test_file).exists():
                self.safe_delete_file(test_file, "Unused test file")
    
    def cleanup_empty_init_files(self):
        """Cleanup __init__.py files yang kosong dan duplikat"""
        print("\n📦 Analyzing __init__.py files...")
        
        init_files = list(self.root_path.rglob("__init__.py"))
        
        for init_file in init_files:
            # Cek ukuran file
            if init_file.stat().st_size <= 1:  # File kosong atau hanya newline
                relative_path = init_file.relative_to(self.root_path)
                # Jangan hapus __init__.py dari direktori penting
                important_dirs = ["colony", "colony/core", "colony/agents", "colony/api"]
                if not any(str(relative_path).startswith(important_dir) for important_dir in important_dirs):
                    self.safe_delete_file(str(relative_path), "Empty __init__.py file")
    
    def generate_cleanup_report(self):
        """Generate laporan cleanup"""
        report = {
            'cleanup_date': str(Path.cwd()),
            'backup_directory': str(self.backup_dir),
            'deleted_files': self.deleted_files,
            'total_deleted': len(self.deleted_files)
        }
        
        # Save report
        report_file = self.root_path / "cleanup_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Cleanup report saved to: {report_file}")
        return report
    
    def run_safe_cleanup(self):
        """Jalankan cleanup lengkap dengan aman"""
        print("🧹 Starting safe file cleanup...")
        print("="*60)
        
        # Buat backup directory
        self.create_backup_dir()
        
        # Jalankan cleanup steps
        self.cleanup_duplicate_readmes()
        self.cleanup_duplicate_launchers()
        self.cleanup_duplicate_registries()
        self.cleanup_duplicate_credential_managers()
        self.cleanup_copy_files()
        self.cleanup_backup_files()
        self.cleanup_test_files()
        self.cleanup_empty_init_files()
        
        # Generate report
        report = self.generate_cleanup_report()
        
        print("\n" + "="*60)
        print("✅ Safe cleanup completed!")
        print(f"📊 Total files processed: {len(self.deleted_files)}")
        print(f"💾 Backup location: {self.backup_dir}")
        print(f"📄 Report: cleanup_report.json")
        
        if self.deleted_files:
            print("\n🗑️ Deleted files:")
            for item in self.deleted_files:
                print(f"   ├── {item['file']} ({item['reason']})")
        
        print("\n⚠️ If anything goes wrong, restore from backup directory!")
        
        return report

def main():
    """Main function"""
    cleanup = SafeFileCleanup()
    
    # Konfirmasi dari user
    print("🚨 SAFE FILE CLEANUP UTILITY")
    print("This will delete duplicate and unnecessary files.")
    print("All files will be backed up before deletion.")
    print()
    
    response = input("Continue with cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cleanup cancelled.")
        return
    
    # Jalankan cleanup
    cleanup.run_safe_cleanup()

if __name__ == "__main__":
    main()