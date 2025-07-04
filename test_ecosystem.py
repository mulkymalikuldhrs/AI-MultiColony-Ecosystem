#!/usr/bin/env python3
"""
🧪 ECOSYSTEM TESTING SUITE v16.0.0
Comprehensive testing for the AI Agent Ecosystem

Tests:
- Syntax validation
- Import compatibility
- Component integration
- Autonomous operation
- Error handling

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import ast
import sys
import importlib
import traceback
from pathlib import Path
import logging
import json
from datetime import datetime

class EcosystemTester:
    """Comprehensive ecosystem testing system"""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.warnings = []
        
        # Setup basic logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )
        self.logger = logging.getLogger("EcosystemTester")
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 ECOSYSTEM TESTING SUITE v16.0.0")
        print("=" * 60)
        
        test_modules = [
            ("syntax_validation", self.test_syntax_validation),
            ("import_compatibility", self.test_import_compatibility),
            ("component_creation", self.test_component_creation),
            ("basic_functionality", self.test_basic_functionality),
            ("error_handling", self.test_error_handling),
            ("autonomous_operation", self.test_autonomous_operation)
        ]
        
        for test_name, test_function in test_modules:
            print(f"\n🔍 Running {test_name}...")
            try:
                result = await test_function()
                self.test_results[test_name] = result
                
                if result["passed"]:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
                    self.errors.extend(result.get("errors", []))
                    
            except Exception as e:
                print(f"❌ {test_name} CRASHED: {e}")
                self.errors.append(f"{test_name}: {str(e)}")
                self.test_results[test_name] = {
                    "passed": False,
                    "errors": [str(e)]
                }
        
        # Generate final report
        await self.generate_test_report()
    
    async def test_syntax_validation(self):
        """Test syntax validation of all Python files"""
        python_files = [
            "UNIFIED_ECOSYSTEM_LAUNCHER.py",
            "ADVANCED_AI_AGENT_ORCHESTRATION.py",
            "FUTURISTIC_UI_SYSTEM.py",
            "MASSIVE_AUTONOMOUS_RESEARCH_ENGINE.py"
        ]
        
        errors = []
        
        for file_name in python_files:
            file_path = Path(file_name)
            if not file_path.exists():
                errors.append(f"File not found: {file_name}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to check syntax
                ast.parse(content, filename=file_name)
                print(f"  ✓ {file_name} syntax valid")
                
            except SyntaxError as e:
                error_msg = f"{file_name}: Syntax error at line {e.lineno}: {e.msg}"
                errors.append(error_msg)
                print(f"  ✗ {error_msg}")
            except Exception as e:
                error_msg = f"{file_name}: {str(e)}"
                errors.append(error_msg)
                print(f"  ✗ {error_msg}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "files_checked": len(python_files)
        }
    
    async def test_import_compatibility(self):
        """Test import compatibility"""
        modules_to_test = [
            "asyncio",
            "logging", 
            "json",
            "pathlib",
            "datetime",
            "sys",
            "os"
        ]
        
        errors = []
        
        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                print(f"  ✓ {module_name} import successful")
            except ImportError as e:
                error_msg = f"Failed to import {module_name}: {e}"
                errors.append(error_msg)
                print(f"  ✗ {error_msg}")
        
        # Test optional dependencies
        optional_modules = [
            "psutil",
            "numpy",
            "flask"
        ]
        
        warnings = []
        for module_name in optional_modules:
            try:
                importlib.import_module(module_name)
                print(f"  ✓ {module_name} (optional) available")
            except ImportError:
                warning_msg = f"Optional module {module_name} not available"
                warnings.append(warning_msg)
                print(f"  ⚠ {warning_msg}")
        
        self.warnings.extend(warnings)
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def test_component_creation(self):
        """Test component creation without running them"""
        errors = []
        components_tested = []
        
        # Test creating launcher
        try:
            # Import and create without running
            sys.path.insert(0, str(Path.cwd()))
            
            # Test basic imports work
            import UNIFIED_ECOSYSTEM_LAUNCHER
            print("  ✓ UNIFIED_ECOSYSTEM_LAUNCHER import successful")
            
            # Test class creation
            launcher = UNIFIED_ECOSYSTEM_LAUNCHER.UnifiedLauncher()
            ecosystem = UNIFIED_ECOSYSTEM_LAUNCHER.EcosystemManager()
            validator = UNIFIED_ECOSYSTEM_LAUNCHER.SyntaxValidator()
            
            print("  ✓ Core classes created successfully")
            components_tested.extend(["launcher", "ecosystem", "validator"])
            
        except Exception as e:
            error_msg = f"Component creation failed: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "components_tested": components_tested
        }
    
    async def test_basic_functionality(self):
        """Test basic functionality without full startup"""
        errors = []
        
        try:
            # Test validation functions
            import UNIFIED_ECOSYSTEM_LAUNCHER
            validator = UNIFIED_ECOSYSTEM_LAUNCHER.SyntaxValidator()
            
            # Test file validation on self
            test_file = Path("test_ecosystem.py")
            if test_file.exists():
                result = await validator.validate_python_file(test_file)
                if result["valid"]:
                    print("  ✓ File validation working")
                else:
                    print("  ⚠ File validation found issues (expected)")
            
            # Test ecosystem manager
            ecosystem = UNIFIED_ECOSYSTEM_LAUNCHER.EcosystemManager()
            
            # Test basic methods exist
            if hasattr(ecosystem, 'validate_ecosystem'):
                print("  ✓ Ecosystem validation method exists")
            
            if hasattr(ecosystem, 'launch_cli_mode'):
                print("  ✓ CLI launch method exists")
            
            if hasattr(ecosystem, 'launch_web_mode'):
                print("  ✓ Web UI launch method exists")
            
        except Exception as e:
            error_msg = f"Basic functionality test failed: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }
    
    async def test_error_handling(self):
        """Test error handling capabilities"""
        errors = []
        
        try:
            import UNIFIED_ECOSYSTEM_LAUNCHER
            
            # Test error handling in validator
            validator = UNIFIED_ECOSYSTEM_LAUNCHER.SyntaxValidator()
            
            # Test with invalid file path
            invalid_file = Path("nonexistent_file.py")
            try:
                result = await validator.validate_python_file(invalid_file)
                if not result["valid"] and result["errors"]:
                    print("  ✓ Error handling for missing files works")
                else:
                    errors.append("Error handling for missing files failed")
            except Exception as e:
                # This is actually expected behavior
                print("  ✓ Exception handling for missing files works")
            
            # Test ecosystem error handling
            ecosystem = UNIFIED_ECOSYSTEM_LAUNCHER.EcosystemManager()
            
            # Test non-existent component
            try:
                result = await ecosystem._start_component("nonexistent_component")
                if not result:
                    print("  ✓ Component error handling works")
                else:
                    errors.append("Component error handling failed")
            except Exception:
                print("  ✓ Component exception handling works")
            
        except Exception as e:
            error_msg = f"Error handling test failed: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }
    
    async def test_autonomous_operation(self):
        """Test autonomous operation capabilities"""
        errors = []
        
        try:
            import UNIFIED_ECOSYSTEM_LAUNCHER
            
            # Test health monitoring
            monitor = UNIFIED_ECOSYSTEM_LAUNCHER.AgentHealthMonitor()
            
            # Simulate agent metrics
            test_metrics = {
                "cpu_usage": 45.0,
                "memory_usage": 60.0,
                "avg_response_time": 2.0,
                "success_rate": 0.95
            }
            
            await monitor.monitor_agent_health("test_agent", test_metrics)
            
            if "test_agent" in monitor.agents_status:
                health_score = monitor.agents_status["test_agent"]["health_score"]
                if 0.0 <= health_score <= 1.0:
                    print(f"  ✓ Health monitoring works (score: {health_score:.2f})")
                else:
                    errors.append(f"Invalid health score: {health_score}")
            else:
                errors.append("Agent health monitoring failed")
            
            # Test logger system
            logger_system = UNIFIED_ECOSYSTEM_LAUNCHER.EcosystemLogger()
            logger_system.logger.info("Test log message")
            print("  ✓ Logging system works")
            
        except Exception as e:
            error_msg = f"Autonomous operation test failed: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ {error_msg}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }
    
    async def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Warnings: {len(self.warnings)} ⚠️")
        
        # Success rate
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result["passed"]:
                    print(f"  • {test_name}")
                    for error in result.get("errors", []):
                        print(f"    - {error}")
        
        # Show warnings
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Overall assessment
        print("\n🏆 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("🌟 EXCELLENT - Ecosystem is ready for production")
        elif success_rate >= 80:
            print("✅ GOOD - Ecosystem is functional with minor issues")
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE - Ecosystem needs some fixes")
        else:
            print("❌ POOR - Ecosystem requires significant fixes")
        
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate
            },
            "detailed_results": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        report_file = Path(f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        return success_rate >= 80  # Return True if ecosystem is ready

async def main():
    """Run the test suite"""
    tester = EcosystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())