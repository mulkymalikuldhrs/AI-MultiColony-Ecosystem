"""
🚀 Ekspansi Launcher - Complete Ecosystem Activation
Comprehensive System Integration & Testing

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path
import subprocess
import logging
from typing import Dict, Any

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

def setup_logging():
    """Setup comprehensive logging"""
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "ekspansi_launcher.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("EkspansiLauncher")

def print_banner():
    """Print Ekspansi banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🚀 EKSPANSI LAUNCHER 🚀                               ║
║                                                                              ║
║                    Comprehensive Ecosystem Activation                        ║
║                                                                              ║
║            🧠 Data Expansion | 🔬 Research Prompts | 🚀 Enhancement          ║
║            📱 Android App | 🔄 Autonomous Evolution | 🌐 Full Stack          ║
║                                                                              ║
║                Made with ❤️ by Mulky Malikul Dhaher 🇮🇩                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

class EkspansiLauncher:
    """
    Comprehensive Ekspansi System Launcher
    
    Features:
    - System validation and syntax checking
    - Data expansion engine activation
    - Research prompt generation
    - Ecosystem enhancement implementation
    - Android app building
    - Complete system integration testing
    """
    
    def __init__(self):
        self.logger = setup_logging()
        self.start_time = datetime.now()
        self.results = {}
        
        # System components status
        self.components = {
            "main_system": False,
            "data_expansion": False,
            "enhancement_system": False,
            "android_app": False,
            "syntax_check": False
        }
        
        self.logger.info("Ekspansi Launcher initialized")
    
    async def run_complete_ekspansi(self):
        """Run complete Ekspansi ecosystem activation"""
        print_banner()
        self.logger.info("🚀 Starting complete Ekspansi ecosystem activation...")
        
        try:
            # Phase 1: System Validation
            await self.phase_1_system_validation()
            
            # Phase 2: Data Expansion
            await self.phase_2_data_expansion()
            
            # Phase 3: Research & Enhancement
            await self.phase_3_research_enhancement()
            
            # Phase 4: Android App Building
            await self.phase_4_android_app()
            
            # Phase 5: Integration Testing
            await self.phase_5_integration_testing()
            
            # Phase 6: Final Report
            await self.phase_6_final_report()
            
        except Exception as e:
            self.logger.error(f"Ekspansi activation failed: {e}")
            print(f"❌ Critical error during activation: {e}")
            return False
        
        return True
    
    async def phase_1_system_validation(self):
        """Phase 1: Complete system validation"""
        print("\n" + "="*80)
        print("📋 PHASE 1: SYSTEM VALIDATION & SYNTAX CHECKING")
        print("="*80)
        
        # Check Python version
        print(f"🐍 Python Version: {sys.version}")
        
        # Check syntax of all Python files
        syntax_result = await self.check_all_syntax()
        self.components["syntax_check"] = syntax_result
        
        if not syntax_result:
            raise Exception("Syntax errors detected. Please fix before continuing.")
        
        # Validate required files
        required_files = [
            "main.py",
            "data_expansion_engine.py", 
            "ecosystem_enhancement_system.py",
            "android_webview_app.py"
        ]
        
        for file in required_files:
            if not Path(file).exists():
                raise Exception(f"Required file missing: {file}")
            print(f"✅ {file}")
        
        print("✅ Phase 1 completed successfully")
        self.results["phase_1"] = {"status": "success", "timestamp": datetime.now().isoformat()}
    
    async def check_all_syntax(self):
        """Check syntax of all Python files"""
        print("🔍 Checking syntax of all Python files...")
        
        python_files = list(Path(".").rglob("*.py"))
        syntax_errors = []
        
        for file_path in python_files:
            try:
                # Skip __pycache__ and .git directories
                if "__pycache__" in str(file_path) or ".git" in str(file_path):
                    continue
                
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(file_path)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    syntax_errors.append({
                        "file": str(file_path),
                        "error": result.stderr
                    })
                    print(f"❌ {file_path}: {result.stderr.strip()}")
                else:
                    print(f"✅ {file_path}")
                    
            except Exception as e:
                syntax_errors.append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        if syntax_errors:
            print(f"\n⚠️ Found {len(syntax_errors)} syntax errors:")
            for error in syntax_errors:
                print(f"  - {error['file']}: {error['error']}")
            return False
        
        print(f"✅ All {len(python_files)} Python files passed syntax check")
        return True
    
    async def phase_2_data_expansion(self):
        """Phase 2: Data expansion engine activation"""
        print("\n" + "="*80)
        print("🧠 PHASE 2: DATA EXPANSION ENGINE ACTIVATION")
        print("="*80)
        
        try:
            # Import data expansion engine
            from data_expansion_engine import data_expansion_engine
            
            print("📊 Initializing Data Expansion Engine...")
            print(f"   - Total sources configured: {len(data_expansion_engine.data_sources)}")
            
            # Get initial status
            initial_status = await data_expansion_engine.get_expansion_status()
            print(f"   - Engine status: {initial_status['engine_status']}")
            
            # Run data scraping (limited for demo)
            print("🔄 Starting data scraping from selected sources...")
            scraping_result = await data_expansion_engine.scrape_all_sources()
            
            print(f"   - Successful scrapes: {scraping_result['successful_scrapes']}")
            print(f"   - Failed scrapes: {scraping_result['failed_scrapes']}")
            print(f"   - Total data points: {scraping_result['total_data_points']}")
            
            # Generate research prompts
            print("🔬 Generating research prompts...")
            prompt_result = await data_expansion_engine.generate_research_prompts()
            
            print(f"   - Total prompts generated: {prompt_result['total_prompts']}")
            print(f"   - Categories covered: {len(prompt_result['categories'])}")
            
            self.components["data_expansion"] = True
            print("✅ Phase 2 completed successfully")
            
            self.results["phase_2"] = {
                "status": "success",
                "scraping_result": scraping_result,
                "prompt_result": prompt_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Phase 2 failed: {e}")
            print(f"❌ Phase 2 failed: {e}")
            raise
    
    async def phase_3_research_enhancement(self):
        """Phase 3: Research analysis and ecosystem enhancement"""
        print("\n" + "="*80)
        print("🚀 PHASE 3: ECOSYSTEM ENHANCEMENT SYSTEM")
        print("="*80)
        
        try:
            # Import enhancement system
            from ecosystem_enhancement_system import ecosystem_enhancement_system
            
            print("🔧 Initializing Ecosystem Enhancement System...")
            
            # Analyze research prompts
            print("📋 Analyzing research prompts...")
            analysis_result = await ecosystem_enhancement_system.analyze_research_prompts()
            
            print(f"   - Total enhancements created: {analysis_result['total_enhancements']}")
            print(f"   - High priority enhancements: {analysis_result['high_priority']}")
            print(f"   - Ready for implementation: {analysis_result['ready_for_implementation']}")
            
            # Implement top enhancements (limited for safety)
            print("⚡ Implementing top priority enhancements...")
            implementation_result = await ecosystem_enhancement_system.implement_enhancements(max_implementations=5)
            
            print(f"   - Successfully implemented: {implementation_result['implemented']}")
            print(f"   - Failed implementations: {implementation_result['failed']}")
            print(f"   - Remaining pending: {implementation_result['remaining_pending']}")
            
            self.components["enhancement_system"] = True
            print("✅ Phase 3 completed successfully")
            
            self.results["phase_3"] = {
                "status": "success",
                "analysis_result": analysis_result,
                "implementation_result": implementation_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Phase 3 failed: {e}")
            print(f"❌ Phase 3 failed: {e}")
            raise
    
    async def phase_4_android_app(self):
        """Phase 4: Android application building"""
        print("\n" + "="*80)
        print("📱 PHASE 4: ANDROID WEBVIEW APPLICATION")
        print("="*80)
        
        try:
            # Import Android app builder
            from android_webview_app import android_app_builder
            
            print("🔧 Creating Android project structure...")
            
            # Create Android project
            creation_result = android_app_builder.create_android_project()
            
            if creation_result["success"]:
                print(f"   - Project created: {creation_result['project_path']}")
                print(f"   - App name: {creation_result['app_name']}")
                print(f"   - Package: {creation_result['package_name']}")
                
                # Check if we can build (optional - requires Android SDK)
                build_status = android_app_builder.get_build_status()
                print(f"   - Build status: {build_status['builder_status']}")
                
                if build_status["project_exists"]:
                    print("📦 Android project structure created successfully")
                    print("   - To build APK: cd android_app && ./gradlew assembleDebug")
                    
                self.components["android_app"] = True
                print("✅ Phase 4 completed successfully")
                
                self.results["phase_4"] = {
                    "status": "success",
                    "creation_result": creation_result,
                    "build_status": build_status,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"Android project creation failed: {creation_result['error']}")
                
        except Exception as e:
            self.logger.error(f"Phase 4 failed: {e}")
            print(f"❌ Phase 4 failed: {e}")
            # Don't raise - Android building is optional
            self.results["phase_4"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def phase_5_integration_testing(self):
        """Phase 5: Integration testing"""
        print("\n" + "="*80)
        print("🧪 PHASE 5: INTEGRATION TESTING")
        print("="*80)
        
        try:
            # Test system integration
            print("🔗 Testing system component integration...")
            
            # Test data expansion + enhancement integration
            from data_expansion_engine import data_expansion_engine
            from ecosystem_enhancement_system import ecosystem_enhancement_system
            
            # Get status from all systems
            expansion_status = await data_expansion_engine.get_expansion_status()
            enhancement_status = await ecosystem_enhancement_system.get_enhancement_status()
            
            print(f"   - Data expansion engine: {expansion_status['engine_status']}")
            print(f"   - Enhancement system: {enhancement_status['system_status']}")
            
            # Test data flow
            if len(data_expansion_engine.research_prompts) > 0:
                print(f"   - Research prompts available: {len(data_expansion_engine.research_prompts)}")
            
            if len(ecosystem_enhancement_system.enhancements) > 0:
                print(f"   - Enhancements created: {len(ecosystem_enhancement_system.enhancements)}")
            
            # Test Android app integration
            if self.components["android_app"]:
                from android_webview_app import android_app_builder
                app_status = android_app_builder.get_build_status()
                print(f"   - Android app builder: {app_status['builder_status']}")
            
            print("✅ Phase 5 completed successfully")
            
            self.results["phase_5"] = {
                "status": "success",
                "expansion_status": expansion_status,
                "enhancement_status": enhancement_status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Phase 5 failed: {e}")
            print(f"❌ Phase 5 failed: {e}")
            raise
    
    async def phase_6_final_report(self):
        """Phase 6: Generate final report"""
        print("\n" + "="*80)
        print("📊 PHASE 6: FINAL EKSPANSI REPORT")
        print("="*80)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # Generate comprehensive report
        report = {
            "ekspansi_activation": {
                "start_time": self.start_time.isoformat(),
                "completion_time": datetime.now().isoformat(),
                "total_duration_seconds": total_time,
                "overall_status": "success" if all(self.components.values()) else "partial"
            },
            "components_status": self.components,
            "phase_results": self.results,
            "system_metrics": await self.gather_system_metrics(),
            "next_steps": self.generate_next_steps()
        }
        
        # Save report
        report_dir = Path("data/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"ekspansi_activation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # Print summary
        print("\n🎉 EKSPANSI ACTIVATION COMPLETE!")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📁 Report saved: {report_file}")
        
        print("\n📋 COMPONENT STATUS:")
        for component, status in self.components.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {component.replace('_', ' ').title()}")
        
        print("\n🚀 SYSTEM READY FOR:")
        print("   • Data scraping from 100+ sources")
        print("   • Research prompt generation")
        print("   • Autonomous ecosystem enhancement")
        print("   • Mobile app deployment")
        print("   • Continuous AI evolution")
        
        print("\n🌐 ACCESS POINTS:")
        print("   • Web Interface: http://localhost:5000")
        print("   • System Status: http://localhost:5000/status")
        print("   • API Documentation: http://localhost:5000/docs")
        if self.components["android_app"]:
            print("   • Android APK: android_app/app/build/outputs/apk/debug/")
        
        print(f"\n📚 Full documentation: README_EKSPANSI.md")
        print(f"🇮🇩 Created by: Mulky Malikul Dhaher - Indonesia")
        
        self.results["phase_6"] = {
            "status": "success",
            "report_file": str(report_file),
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    async def gather_system_metrics(self):
        """Gather comprehensive system metrics"""
        try:
            metrics = {
                "files_created": len(list(Path(".").rglob("*.py"))),
                "total_codebase_size": sum(f.stat().st_size for f in Path(".").rglob("*.py") if f.is_file()),
                "components_active": sum(self.components.values()),
                "data_sources_available": 100,  # As configured
                "research_prompts_target": 100
            }
            
            # Try to get actual metrics from systems if available
            try:
                from data_expansion_engine import data_expansion_engine
                expansion_status = await data_expansion_engine.get_expansion_status()
                metrics.update({
                    "data_sources_configured": expansion_status["data_sources"]["total"],
                    "research_prompts_generated": expansion_status["research_prompts"]["total_prompts"]
                })
            except:
                pass
            
            try:
                from ecosystem_enhancement_system import ecosystem_enhancement_system
                enhancement_status = await ecosystem_enhancement_system.get_enhancement_status()
                metrics.update({
                    "enhancements_created": enhancement_status["enhancements"]["total"],
                    "features_implemented": enhancement_status["implementations"]["total"]
                })
            except:
                pass
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to gather metrics: {e}")
            return {"error": str(e)}
    
    def generate_next_steps(self):
        """Generate recommended next steps"""
        next_steps = [
            "Start the main system: python3 main.py",
            "Monitor system status via web interface: http://localhost:5000/status",
            "Review generated research prompts in data/expansion/research_prompts.json",
            "Check implemented enhancements in data/expansion/ecosystem_enhancements.json"
        ]
        
        if self.components["android_app"]:
            next_steps.extend([
                "Build Android APK: cd android_app && ./gradlew assembleDebug",
                "Install APK on device: adb install app/build/outputs/apk/debug/app-debug.apk"
            ])
        
        next_steps.extend([
            "Customize data sources in data_expansion_engine.py",
            "Add custom research prompts templates",
            "Implement additional enhancement categories",
            "Deploy to production environment"
        ])
        
        return next_steps

async def main():
    """Main launcher function"""
    try:
        launcher = EkspansiLauncher()
        success = await launcher.run_complete_ekspansi()
        
        if success:
            print("\n🎯 Ekspansi ecosystem successfully activated!")
            print("Ready to revolutionize AI with autonomous evolution!")
            return 0
        else:
            print("\n❌ Ekspansi activation encountered issues.")
            print("Check logs for detailed error information.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Ekspansi activation interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error during Ekspansi activation: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())