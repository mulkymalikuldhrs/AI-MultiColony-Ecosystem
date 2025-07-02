"""
🔍 Quality Control Specialist - Visual and Analytical Assessment Agent
Advanced AI agent for comprehensive quality control, analysis, and validation

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import logging
import hashlib
import cv2
import numpy as np
import base64
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import requests
import subprocess
import threading
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

@dataclass
class QualityAssessment:
    """Quality assessment result data structure"""
    assessment_id: str
    item_type: str  # code, image, document, system, process
    assessment_type: str  # visual, analytical, performance, security
    score: float  # 0-100 quality score
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    assessment_time: datetime
    assessor: str = "Quality Control Specialist"
    metadata: Dict[str, Any] = None

@dataclass
class QualityMetrics:
    """Quality metrics tracking"""
    total_assessments: int
    average_score: float
    pass_rate: float
    critical_issues: int
    improvement_trends: Dict[str, float]
    last_updated: datetime

class QualityControlSpecialist:
    """
    Quality Control Specialist: Comprehensive quality assessment and validation
    
    Capabilities:
    - 🔍 Visual quality assessment
    - 📊 Analytical quality evaluation
    - 🧪 Performance testing and analysis
    - 🔒 Security quality validation
    - 📈 Quality metrics tracking
    - 🎯 Issue detection and classification
    - 💡 Improvement recommendations
    - 📋 Quality reporting and documentation
    """
    
    def __init__(self):
        self.agent_id = "quality_control_specialist"
        self.name = "Quality Control Specialist"
        self.status = "initializing"
        self.version = "1.0.0"
        self.start_time = datetime.now()
        
        # Core capabilities
        self.capabilities = [
            "visual_assessment",
            "analytical_evaluation",
            "performance_testing",
            "security_validation",
            "metrics_tracking",
            "issue_detection",
            "improvement_analysis",
            "quality_reporting"
        ]
        
        # Assessment history
        self.assessments = {}
        self.quality_metrics = QualityMetrics(
            total_assessments=0,
            average_score=0.0,
            pass_rate=0.0,
            critical_issues=0,
            improvement_trends={},
            last_updated=datetime.now()
        )
        
        # Quality standards
        self.quality_standards = {
            "code": {
                "minimum_score": 75.0,
                "critical_issues": ["security_vulnerability", "memory_leak", "infinite_loop"],
                "best_practices": ["documentation", "testing", "error_handling", "code_style"]
            },
            "image": {
                "minimum_score": 80.0,
                "quality_factors": ["resolution", "clarity", "composition", "lighting"],
                "technical_requirements": ["format", "size", "compression"]
            },
            "system": {
                "minimum_score": 85.0,
                "performance_metrics": ["response_time", "throughput", "reliability"],
                "security_checks": ["authentication", "authorization", "encryption"]
            },
            "process": {
                "minimum_score": 70.0,
                "efficiency_metrics": ["automation_level", "error_rate", "completion_time"],
                "compliance_checks": ["standards_adherence", "documentation", "traceability"]
            }
        }
        
        # Assessment tools
        self.assessment_tools = {
            "code_analyzers": ["pylint", "flake8", "bandit", "mypy"],
            "image_processors": ["opencv", "pillow", "skimage"],
            "performance_testers": ["pytest", "locust", "ab"],
            "security_scanners": ["semgrep", "safety", "pip-audit"]
        }
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize assessment environment
        self.initialize_assessment_environment()
        
        self.logger.info("Quality Control Specialist initialized successfully")
        self.status = "ready"
    
    def setup_logging(self):
        """Setup logging for Quality Control Specialist"""
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "quality_control.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("QualityControlSpecialist")
    
    def initialize_assessment_environment(self):
        """Initialize quality assessment environment"""
        # Create assessment directories
        assessment_dirs = [
            "data/quality_assessments",
            "data/quality_reports", 
            "data/quality_metrics",
            "data/quality_standards"
        ]
        
        for directory in assessment_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Load existing quality standards if available
        self.load_quality_standards()
    
    def load_quality_standards(self):
        """Load custom quality standards"""
        standards_file = Path("data/quality_standards/custom_standards.json")
        if standards_file.exists():
            try:
                with open(standards_file, 'r') as f:
                    custom_standards = json.load(f)
                    self.quality_standards.update(custom_standards)
                    self.logger.info("Custom quality standards loaded")
            except Exception as e:
                self.logger.error(f"Failed to load custom standards: {e}")
    
    async def assess_code_quality(self, code_data: Union[str, Dict[str, Any]]) -> QualityAssessment:
        """Assess code quality using multiple analysis techniques"""
        self.logger.info("Starting code quality assessment")
        
        assessment_id = hashlib.md5(f"code_{datetime.now()}".encode()).hexdigest()[:8]
        issues_found = []
        recommendations = []
        
        try:
            # Extract code content
            if isinstance(code_data, str):
                code_content = code_data
                file_path = "temp_code.py"
            else:
                code_content = code_data.get("content", "")
                file_path = code_data.get("file_path", "temp_code.py")
            
            # Static code analysis
            static_analysis = await self._perform_static_analysis(code_content, file_path)
            issues_found.extend(static_analysis.get("issues", []))
            
            # Code style analysis
            style_analysis = await self._analyze_code_style(code_content)
            issues_found.extend(style_analysis.get("issues", []))
            
            # Security analysis
            security_analysis = await self._analyze_code_security(code_content)
            issues_found.extend(security_analysis.get("issues", []))
            
            # Complexity analysis
            complexity_analysis = await self._analyze_code_complexity(code_content)
            issues_found.extend(complexity_analysis.get("issues", []))
            
            # Generate recommendations
            recommendations = self._generate_code_recommendations(issues_found)
            
            # Calculate quality score
            quality_score = self._calculate_code_quality_score(issues_found, code_content)
            
            assessment = QualityAssessment(
                assessment_id=assessment_id,
                item_type="code",
                assessment_type="analytical",
                score=quality_score,
                issues_found=issues_found,
                recommendations=recommendations,
                assessment_time=datetime.now(),
                metadata={
                    "file_path": file_path,
                    "lines_of_code": len(code_content.split('\n')),
                    "analysis_tools": list(self.assessment_tools["code_analyzers"])
                }
            )
            
            self.assessments[assessment_id] = assessment
            await self._update_quality_metrics(assessment)
            
            self.logger.info(f"Code quality assessment completed: {quality_score:.1f}/100")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Code quality assessment failed: {e}")
            raise
    
    async def assess_image_quality(self, image_data: Union[str, bytes, Dict[str, Any]]) -> QualityAssessment:
        """Assess image quality using computer vision techniques"""
        self.logger.info("Starting image quality assessment")
        
        assessment_id = hashlib.md5(f"image_{datetime.now()}".encode()).hexdigest()[:8]
        issues_found = []
        recommendations = []
        
        try:
            # Load image
            if isinstance(image_data, str):
                # Assume it's a file path or base64 encoded
                if image_data.startswith('data:image'):
                    # Base64 encoded image
                    image_bytes = base64.b64decode(image_data.split(',')[1])
                    image = Image.open(io.BytesIO(image_bytes))
                else:
                    # File path
                    image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                # Dictionary with image data
                image_path = image_data.get("path")
                if image_path:
                    image = Image.open(image_path)
                else:
                    raise ValueError("Invalid image data provided")
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Technical quality analysis
            technical_analysis = await self._analyze_image_technical_quality(img_array, image)
            issues_found.extend(technical_analysis.get("issues", []))
            
            # Visual quality analysis
            visual_analysis = await self._analyze_image_visual_quality(img_array)
            issues_found.extend(visual_analysis.get("issues", []))
            
            # Composition analysis
            composition_analysis = await self._analyze_image_composition(img_array)
            issues_found.extend(composition_analysis.get("issues", []))
            
            # Generate recommendations
            recommendations = self._generate_image_recommendations(issues_found, image)
            
            # Calculate quality score
            quality_score = self._calculate_image_quality_score(issues_found, img_array)
            
            assessment = QualityAssessment(
                assessment_id=assessment_id,
                item_type="image",
                assessment_type="visual",
                score=quality_score,
                issues_found=issues_found,
                recommendations=recommendations,
                assessment_time=datetime.now(),
                metadata={
                    "dimensions": f"{image.width}x{image.height}",
                    "format": image.format,
                    "mode": image.mode,
                    "file_size": len(img_array.tobytes()) if hasattr(img_array, 'tobytes') else 0
                }
            )
            
            self.assessments[assessment_id] = assessment
            await self._update_quality_metrics(assessment)
            
            self.logger.info(f"Image quality assessment completed: {quality_score:.1f}/100")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Image quality assessment failed: {e}")
            raise
    
    async def assess_system_quality(self, system_data: Dict[str, Any]) -> QualityAssessment:
        """Assess system quality including performance, security, and reliability"""
        self.logger.info("Starting system quality assessment")
        
        assessment_id = hashlib.md5(f"system_{datetime.now()}".encode()).hexdigest()[:8]
        issues_found = []
        recommendations = []
        
        try:
            # Performance assessment
            if "performance_metrics" in system_data:
                performance_analysis = await self._analyze_system_performance(system_data["performance_metrics"])
                issues_found.extend(performance_analysis.get("issues", []))
            
            # Security assessment
            if "security_config" in system_data:
                security_analysis = await self._analyze_system_security(system_data["security_config"])
                issues_found.extend(security_analysis.get("issues", []))
            
            # Reliability assessment
            if "reliability_metrics" in system_data:
                reliability_analysis = await self._analyze_system_reliability(system_data["reliability_metrics"])
                issues_found.extend(reliability_analysis.get("issues", []))
            
            # Scalability assessment
            if "scalability_data" in system_data:
                scalability_analysis = await self._analyze_system_scalability(system_data["scalability_data"])
                issues_found.extend(scalability_analysis.get("issues", []))
            
            # Generate recommendations
            recommendations = self._generate_system_recommendations(issues_found)
            
            # Calculate quality score
            quality_score = self._calculate_system_quality_score(issues_found, system_data)
            
            assessment = QualityAssessment(
                assessment_id=assessment_id,
                item_type="system",
                assessment_type="performance",
                score=quality_score,
                issues_found=issues_found,
                recommendations=recommendations,
                assessment_time=datetime.now(),
                metadata=system_data
            )
            
            self.assessments[assessment_id] = assessment
            await self._update_quality_metrics(assessment)
            
            self.logger.info(f"System quality assessment completed: {quality_score:.1f}/100")
            return assessment
            
        except Exception as e:
            self.logger.error(f"System quality assessment failed: {e}")
            raise
    
    async def assess_process_quality(self, process_data: Dict[str, Any]) -> QualityAssessment:
        """Assess process quality including efficiency, compliance, and automation"""
        self.logger.info("Starting process quality assessment")
        
        assessment_id = hashlib.md5(f"process_{datetime.now()}".encode()).hexdigest()[:8]
        issues_found = []
        recommendations = []
        
        try:
            # Efficiency analysis
            efficiency_analysis = await self._analyze_process_efficiency(process_data)
            issues_found.extend(efficiency_analysis.get("issues", []))
            
            # Compliance analysis
            compliance_analysis = await self._analyze_process_compliance(process_data)
            issues_found.extend(compliance_analysis.get("issues", []))
            
            # Automation analysis
            automation_analysis = await self._analyze_process_automation(process_data)
            issues_found.extend(automation_analysis.get("issues", []))
            
            # Generate recommendations
            recommendations = self._generate_process_recommendations(issues_found)
            
            # Calculate quality score
            quality_score = self._calculate_process_quality_score(issues_found, process_data)
            
            assessment = QualityAssessment(
                assessment_id=assessment_id,
                item_type="process",
                assessment_type="analytical",
                score=quality_score,
                issues_found=issues_found,
                recommendations=recommendations,
                assessment_time=datetime.now(),
                metadata=process_data
            )
            
            self.assessments[assessment_id] = assessment
            await self._update_quality_metrics(assessment)
            
            self.logger.info(f"Process quality assessment completed: {quality_score:.1f}/100")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Process quality assessment failed: {e}")
            raise
    
    async def generate_quality_report(self, time_period: str = "week") -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        self.logger.info(f"Generating quality report for {time_period}")
        
        # Determine time range
        now = datetime.now()
        if time_period == "day":
            start_time = now - timedelta(days=1)
        elif time_period == "week":
            start_time = now - timedelta(weeks=1)
        elif time_period == "month":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(weeks=1)  # Default to week
        
        # Filter assessments by time period
        period_assessments = [
            assessment for assessment in self.assessments.values()
            if assessment.assessment_time >= start_time
        ]
        
        if not period_assessments:
            return {
                "period": time_period,
                "total_assessments": 0,
                "message": "No assessments found in the specified period"
            }
        
        # Calculate statistics
        total_assessments = len(period_assessments)
        average_score = sum(a.score for a in period_assessments) / total_assessments
        passing_assessments = len([a for a in period_assessments if a.score >= 75.0])
        pass_rate = (passing_assessments / total_assessments) * 100
        
        # Category breakdown
        category_stats = {}
        for assessment in period_assessments:
            category = assessment.item_type
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "average_score": 0.0,
                    "scores": []
                }
            category_stats[category]["count"] += 1
            category_stats[category]["scores"].append(assessment.score)
        
        # Calculate category averages
        for category, stats in category_stats.items():
            stats["average_score"] = sum(stats["scores"]) / len(stats["scores"])
        
        # Top issues
        all_issues = []
        for assessment in period_assessments:
            all_issues.extend(assessment.issues_found)
        
        issue_frequency = {}
        for issue in all_issues:
            issue_type = issue.get("type", "unknown")
            issue_frequency[issue_type] = issue_frequency.get(issue_type, 0) + 1
        
        top_issues = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Quality trends
        daily_scores = {}
        for assessment in period_assessments:
            day = assessment.assessment_time.date().isoformat()
            if day not in daily_scores:
                daily_scores[day] = []
            daily_scores[day].append(assessment.score)
        
        trend_data = {}
        for day, scores in daily_scores.items():
            trend_data[day] = {
                "average_score": sum(scores) / len(scores),
                "assessments_count": len(scores)
            }
        
        # Generate report
        report = {
            "report_id": hashlib.md5(f"report_{datetime.now()}".encode()).hexdigest()[:8],
            "generated_at": now.isoformat(),
            "period": time_period,
            "period_start": start_time.isoformat(),
            "period_end": now.isoformat(),
            "summary": {
                "total_assessments": total_assessments,
                "average_score": round(average_score, 2),
                "pass_rate": round(pass_rate, 2),
                "passing_assessments": passing_assessments
            },
            "category_breakdown": category_stats,
            "top_issues": top_issues,
            "quality_trends": trend_data,
            "recommendations": self._generate_period_recommendations(period_assessments)
        }
        
        # Save report
        report_file = Path(f"data/quality_reports/quality_report_{now.strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Quality report generated: {report_file}")
        return report
    
    async def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current quality metrics"""
        await self._update_quality_metrics()
        
        return {
            "total_assessments": self.quality_metrics.total_assessments,
            "average_score": round(self.quality_metrics.average_score, 2),
            "pass_rate": round(self.quality_metrics.pass_rate, 2),
            "critical_issues": self.quality_metrics.critical_issues,
            "improvement_trends": self.quality_metrics.improvement_trends,
            "last_updated": self.quality_metrics.last_updated.isoformat(),
            "agent_status": self.status,
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600
        }
    
    # Private helper methods
    
    async def _perform_static_analysis(self, code_content: str, file_path: str) -> Dict[str, Any]:
        """Perform static code analysis"""
        issues = []
        
        try:
            # Basic syntax check
            try:
                compile(code_content, file_path, 'exec')
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "severity": "critical",
                    "description": f"Syntax error: {e.msg}",
                    "line": e.lineno
                })
            
            # Check for common issues
            lines = code_content.split('\n')
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Check for security issues
                if 'eval(' in line or 'exec(' in line:
                    issues.append({
                        "type": "security_vulnerability",
                        "severity": "high",
                        "description": "Use of eval() or exec() can be dangerous",
                        "line": i
                    })
                
                # Check for code quality issues
                if len(line) > 120:
                    issues.append({
                        "type": "line_too_long",
                        "severity": "low",
                        "description": f"Line exceeds 120 characters ({len(line)} chars)",
                        "line": i
                    })
                
                # Check for TODO/FIXME comments
                if 'TODO' in line_stripped or 'FIXME' in line_stripped:
                    issues.append({
                        "type": "todo_comment",
                        "severity": "low",
                        "description": "Unresolved TODO/FIXME comment",
                        "line": i
                    })
            
            return {"issues": issues}
            
        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")
            return {"issues": []}
    
    async def _update_quality_metrics(self, assessment: QualityAssessment = None):
        """Update overall quality metrics"""
        try:
            if not self.assessments:
                return
            
            assessments = list(self.assessments.values())
            
            self.quality_metrics.total_assessments = len(assessments)
            self.quality_metrics.average_score = sum(a.score for a in assessments) / len(assessments)
            
            passing_assessments = len([a for a in assessments if a.score >= 75.0])
            self.quality_metrics.pass_rate = (passing_assessments / len(assessments)) * 100
            
            # Count critical issues
            critical_issues = 0
            for assessment in assessments:
                for issue in assessment.issues_found:
                    if issue.get("severity") == "critical":
                        critical_issues += 1
            self.quality_metrics.critical_issues = critical_issues
            
            self.quality_metrics.last_updated = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Failed to update quality metrics: {e}")
    
    def _calculate_code_quality_score(self, issues: List[Dict[str, Any]], code_content: str) -> float:
        """Calculate code quality score based on issues found"""
        base_score = 100.0
        
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "critical":
                base_score -= 20
            elif severity == "high":
                base_score -= 10
            elif severity == "medium":
                base_score -= 5
            else:  # low
                base_score -= 2
        
        # Bonus for good practices
        lines = code_content.split('\n')
        has_docstring = any('"""' in line or "'''" in line for line in lines[:10])
        has_type_hints = any(':' in line and '->' in line for line in lines)
        
        if has_docstring:
            base_score += 5
        if has_type_hints:
            base_score += 5
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_code_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate code improvement recommendations"""
        recommendations = []
        
        issue_types = [issue.get("type") for issue in issues]
        
        if "syntax_error" in issue_types:
            recommendations.append("Fix syntax errors before proceeding with other improvements")
        
        if "security_vulnerability" in issue_types:
            recommendations.append("Address security vulnerabilities immediately")
            recommendations.append("Consider using safer alternatives to eval() and exec()")
        
        if "line_too_long" in issue_types:
            recommendations.append("Break long lines into multiple lines for better readability")
        
        if len([i for i in issues if i.get("severity") == "critical"]) > 0:
            recommendations.append("Focus on critical issues first as they may cause system failures")
        
        return recommendations

# Global instance
quality_control_specialist = QualityControlSpecialist()

# Export for use by other modules
__all__ = ['QualityControlSpecialist', 'quality_control_specialist', 'QualityAssessment', 'QualityMetrics']
