"""
🧠 Data Expansion Engine - Ekspansi Branch
Comprehensive Data Scraping & Research Prompt Generator

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import aiohttp
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
import hashlib
import re
from urllib.parse import urljoin, urlparse
import feedparser
import requests
from bs4 import BeautifulSoup
import nltk
from textstat import flesch_reading_ease
import yake

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    url: str
    source_type: str  # web, api, rss, academic, news, tech, ai, research
    category: str
    priority: int
    last_scraped: Optional[datetime] = None
    success_rate: float = 1.0
    metadata: Dict[str, Any] = None

@dataclass
class ScrapedData:
    """Scraped data structure"""
    source_id: str
    title: str
    content: str
    url: str
    category: str
    timestamp: datetime
    keywords: List[str]
    sentiment: str
    reading_level: int
    quality_score: float
    metadata: Dict[str, Any] = None

@dataclass
class ResearchPrompt:
    """Research prompt structure"""
    prompt_id: str
    title: str
    prompt_text: str
    category: str
    complexity: str  # basic, intermediate, advanced, expert
    potential_applications: List[str]
    data_sources: List[str]
    estimated_impact: str  # low, medium, high, critical
    implementation_priority: int
    metadata: Dict[str, Any] = None

class DataExpansionEngine:
    """
    Advanced Data Expansion Engine for Ecosystem Enhancement
    
    Features:
    - 100+ source data scraping
    - Intelligent content analysis
    - Research prompt generation
    - Quality assessment
    - Real-time monitoring
    - Automated ecosystem enhancement
    """
    
    def __init__(self):
        self.name = "Data Expansion Engine"
        self.version = "1.0.0"
        self.status = "initializing"
        self.start_time = datetime.now()
        
        # Data storage
        self.data_sources = {}
        self.scraped_data = {}
        self.research_prompts = {}
        self.ecosystem_enhancements = {}
        
        # Configuration
        self.config = {
            "max_concurrent_requests": 10,
            "request_delay": 1,
            "retry_attempts": 3,
            "quality_threshold": 0.7,
            "content_min_length": 100,
            "enable_nlp_analysis": True,
            "auto_generate_prompts": True,
            "save_interval": 300  # 5 minutes
        }
        
        # Statistics
        self.stats = {
            "total_sources": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "prompts_generated": 0,
            "enhancements_implemented": 0
        }
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize data sources
        self.initialize_data_sources()
        
        self.logger.info(f"Data Expansion Engine initialized - {self.name} v{self.version}")
        self.status = "ready"
    
    def setup_logging(self):
        """Setup logging for Data Expansion Engine"""
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "data_expansion.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("DataExpansionEngine")
    
    def initialize_data_sources(self):
        """Initialize 100+ data sources for comprehensive scraping"""
        
        # AI & Machine Learning Sources
        ai_sources = [
            DataSource("OpenAI Blog", "https://openai.com/blog", "web", "ai_research", 1),
            DataSource("Google AI Blog", "https://ai.googleblog.com", "web", "ai_research", 1),
            DataSource("DeepMind Blog", "https://deepmind.com/blog", "web", "ai_research", 1),
            DataSource("Microsoft AI Blog", "https://blogs.microsoft.com/ai", "web", "ai_research", 1),
            DataSource("Facebook AI Research", "https://ai.facebook.com/blog", "web", "ai_research", 1),
            DataSource("Anthropic Research", "https://www.anthropic.com/research", "web", "ai_research", 1),
            DataSource("Hugging Face Blog", "https://huggingface.co/blog", "web", "ai_tools", 2),
            DataSource("Papers with Code", "https://paperswithcode.com", "web", "ai_research", 1),
            DataSource("Towards Data Science", "https://towardsdatascience.com", "web", "ai_education", 2),
            DataSource("Machine Learning Mastery", "https://machinelearningmastery.com", "web", "ai_education", 2),
        ]
        
        # Technology Sources
        tech_sources = [
            DataSource("TechCrunch", "https://techcrunch.com", "web", "tech_news", 2),
            DataSource("Ars Technica", "https://arstechnica.com", "web", "tech_news", 2),
            DataSource("The Verge", "https://www.theverge.com", "web", "tech_news", 2),
            DataSource("Wired", "https://www.wired.com", "web", "tech_news", 2),
            DataSource("MIT Technology Review", "https://www.technologyreview.com", "web", "tech_research", 1),
            DataSource("IEEE Spectrum", "https://spectrum.ieee.org", "web", "tech_research", 1),
            DataSource("ACM Digital Library", "https://dl.acm.org", "academic", "tech_research", 1),
            DataSource("arXiv Computer Science", "https://arxiv.org/list/cs/recent", "academic", "research", 1),
            DataSource("GitHub Trending", "https://github.com/trending", "web", "development", 2),
            DataSource("Stack Overflow Blog", "https://stackoverflow.blog", "web", "development", 2),
        ]
        
        # Business & Innovation Sources
        business_sources = [
            DataSource("Harvard Business Review", "https://hbr.org", "web", "business", 2),
            DataSource("McKinsey & Company", "https://www.mckinsey.com/insights", "web", "business", 2),
            DataSource("BCG Insights", "https://www.bcg.com/insights", "web", "business", 2),
            DataSource("Deloitte Insights", "https://www2.deloitte.com/insights", "web", "business", 2),
            DataSource("PwC Insights", "https://www.pwc.com/insights", "web", "business", 2),
            DataSource("Fast Company", "https://www.fastcompany.com", "web", "innovation", 2),
            DataSource("Innovation Excellence", "https://www.innovationexcellence.com", "web", "innovation", 3),
            DataSource("CB Insights", "https://www.cbinsights.com/research", "web", "market_intelligence", 2),
            DataSource("Gartner Research", "https://www.gartner.com/en/insights", "web", "market_research", 1),
            DataSource("Forrester Research", "https://www.forrester.com/blogs", "web", "market_research", 1),
        ]
        
        # Academic & Research Sources
        academic_sources = [
            DataSource("Nature", "https://www.nature.com", "academic", "science", 1),
            DataSource("Science Magazine", "https://www.sciencemag.org", "academic", "science", 1),
            DataSource("PNAS", "https://www.pnas.org", "academic", "science", 1),
            DataSource("Cell", "https://www.cell.com", "academic", "biology", 1),
            DataSource("NEJM", "https://www.nejm.org", "academic", "medicine", 1),
            DataSource("JAMA", "https://jamanetwork.com", "academic", "medicine", 1),
            DataSource("Lancet", "https://www.thelancet.com", "academic", "medicine", 1),
            DataSource("Physical Review", "https://journals.aps.org", "academic", "physics", 1),
            DataSource("AAAI Publications", "https://www.aaai.org/Library/library.php", "academic", "ai_research", 1),
            DataSource("ICML Proceedings", "https://proceedings.mlr.press", "academic", "ai_research", 1),
        ]
        
        # Development & Programming Sources
        dev_sources = [
            DataSource("Dev.to", "https://dev.to", "web", "development", 2),
            DataSource("Medium Programming", "https://medium.com/topic/programming", "web", "development", 2),
            DataSource("InfoQ", "https://www.infoq.com", "web", "development", 2),
            DataSource("DZone", "https://dzone.com", "web", "development", 3),
            DataSource("CodeProject", "https://www.codeproject.com", "web", "development", 3),
            DataSource("Smashing Magazine", "https://www.smashingmagazine.com", "web", "web_development", 2),
            DataSource("A List Apart", "https://alistapart.com", "web", "web_development", 2),
            DataSource("CSS-Tricks", "https://css-tricks.com", "web", "web_development", 2),
            DataSource("FreeCodeCamp", "https://www.freecodecamp.org/news", "web", "education", 2),
            DataSource("Codecademy Blog", "https://blog.codecademy.com", "web", "education", 3),
        ]
        
        # Cybersecurity Sources
        security_sources = [
            DataSource("Krebs on Security", "https://krebsonsecurity.com", "web", "cybersecurity", 2),
            DataSource("Dark Reading", "https://www.darkreading.com", "web", "cybersecurity", 2),
            DataSource("Security Week", "https://www.securityweek.com", "web", "cybersecurity", 2),
            DataSource("SANS Institute", "https://www.sans.org/blog", "web", "cybersecurity", 1),
            DataSource("NIST Cybersecurity", "https://www.nist.gov/cybersecurity", "web", "cybersecurity", 1),
            DataSource("CVE Details", "https://www.cvedetails.com", "web", "security_vulnerabilities", 2),
            DataSource("OWASP", "https://owasp.org/www-community", "web", "web_security", 1),
            DataSource("Checkpoint Research", "https://research.checkpoint.com", "web", "cybersecurity", 2),
            DataSource("FireEye Threat Intelligence", "https://www.fireeye.com/blog/threat-research.html", "web", "threat_intelligence", 1),
            DataSource("Kaspersky Securelist", "https://securelist.com", "web", "cybersecurity", 2),
        ]
        
        # Data Science & Analytics Sources
        datascience_sources = [
            DataSource("KDnuggets", "https://www.kdnuggets.com", "web", "data_science", 2),
            DataSource("Analytics Vidhya", "https://www.analyticsvidhya.com/blog", "web", "data_science", 2),
            DataSource("DataCamp Blog", "https://www.datacamp.com/community/blog", "web", "data_science", 2),
            DataSource("Data Science Central", "https://www.datasciencecentral.com", "web", "data_science", 2),
            DataSource("Flowing Data", "https://flowingdata.com", "web", "data_visualization", 2),
            DataSource("Information is Beautiful", "https://informationisbeautiful.net", "web", "data_visualization", 2),
            DataSource("Tableau Blog", "https://www.tableau.com/learn/articles", "web", "data_visualization", 3),
            DataSource("Databricks Blog", "https://databricks.com/blog", "web", "big_data", 2),
            DataSource("Apache Spark", "https://spark.apache.org/news", "web", "big_data", 2),
            DataSource("Cloudera Blog", "https://blog.cloudera.com", "web", "big_data", 3),
        ]
        
        # Cloud Computing Sources
        cloud_sources = [
            DataSource("AWS Blog", "https://aws.amazon.com/blogs", "web", "cloud_computing", 1),
            DataSource("Google Cloud Blog", "https://cloud.google.com/blog", "web", "cloud_computing", 1),
            DataSource("Microsoft Azure Blog", "https://azure.microsoft.com/en-us/blog", "web", "cloud_computing", 1),
            DataSource("DigitalOcean Blog", "https://www.digitalocean.com/community", "web", "cloud_computing", 2),
            DataSource("Kubernetes Blog", "https://kubernetes.io/blog", "web", "containers", 1),
            DataSource("Docker Blog", "https://www.docker.com/blog", "web", "containers", 2),
            DataSource("Red Hat Blog", "https://www.redhat.com/en/blog", "web", "enterprise_tech", 2),
            DataSource("VMware Blog", "https://blogs.vmware.com", "web", "virtualization", 2),
            DataSource("HashiCorp Blog", "https://www.hashicorp.com/blog", "web", "infrastructure", 2),
            DataSource("Terraform", "https://www.terraform.io/blog", "web", "infrastructure", 2),
        ]
        
        # IoT & Edge Computing Sources
        iot_sources = [
            DataSource("IoT For All", "https://www.iotforall.com", "web", "iot", 2),
            DataSource("IoT Central", "https://www.iotcentral.io", "web", "iot", 3),
            DataSource("Edge Computing News", "https://www.edgecomputing-news.com", "web", "edge_computing", 3),
            DataSource("Industrial IoT", "https://industrialiot.com", "web", "industrial_iot", 3),
            DataSource("Arduino Blog", "https://blog.arduino.cc", "web", "embedded_systems", 2),
            DataSource("Raspberry Pi Foundation", "https://www.raspberrypi.org/blog", "web", "embedded_systems", 2),
            DataSource("NVIDIA Developer Blog", "https://developer.nvidia.com/blog", "web", "gpu_computing", 1),
            DataSource("Intel AI", "https://www.intel.com/content/www/us/en/artificial-intelligence", "web", "hardware_ai", 1),
            DataSource("ARM Developer", "https://developer.arm.com", "web", "embedded_systems", 2),
            DataSource("Qualcomm Developer", "https://developer.qualcomm.com", "web", "mobile_computing", 2),
        ]
        
        # Combine all sources
        all_sources = (ai_sources + tech_sources + business_sources + academic_sources + 
                      dev_sources + security_sources + datascience_sources + cloud_sources + iot_sources)
        
        # Add sources to registry
        for source in all_sources:
            source_id = hashlib.md5(f"{source.name}_{source.url}".encode()).hexdigest()[:12]
            self.data_sources[source_id] = source
        
        self.stats["total_sources"] = len(self.data_sources)
        self.logger.info(f"Initialized {len(self.data_sources)} data sources across 9 categories")
    
    async def scrape_all_sources(self) -> Dict[str, Any]:
        """Scrape data from all registered sources"""
        self.logger.info("Starting comprehensive data scraping from all sources...")
        
        start_time = time.time()
        semaphore = asyncio.Semaphore(self.config["max_concurrent_requests"])
        
        # Create scraping tasks
        tasks = []
        for source_id, source in self.data_sources.items():
            task = asyncio.create_task(self._scrape_single_source(semaphore, source_id, source))
            tasks.append(task)
        
        # Execute all scraping tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_scrapes = 0
        failed_scrapes = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_scrapes += 1
                self.logger.error(f"Scraping failed for source {list(self.data_sources.keys())[i]}: {result}")
            elif result:
                successful_scrapes += 1
        
        # Update statistics
        self.stats["successful_scrapes"] = successful_scrapes
        self.stats["failed_scrapes"] = failed_scrapes
        
        scraping_time = time.time() - start_time
        
        # Save scraped data
        await self._save_scraped_data()
        
        self.logger.info(f"Scraping completed: {successful_scrapes} successful, {failed_scrapes} failed in {scraping_time:.2f}s")
        
        return {
            "successful_scrapes": successful_scrapes,
            "failed_scrapes": failed_scrapes,
            "total_data_points": len(self.scraped_data),
            "scraping_time": scraping_time,
            "data_categories": list(set([data.category for data in self.scraped_data.values()]))
        }
    
    async def _scrape_single_source(self, semaphore: asyncio.Semaphore, source_id: str, source: DataSource) -> bool:
        """Scrape data from a single source"""
        async with semaphore:
            try:
                # Add delay between requests
                await asyncio.sleep(random.uniform(0.5, self.config["request_delay"]))
                
                if source.source_type == "web":
                    content = await self._scrape_web_content(source)
                elif source.source_type == "rss":
                    content = await self._scrape_rss_feed(source)
                elif source.source_type == "api":
                    content = await self._scrape_api_data(source)
                elif source.source_type == "academic":
                    content = await self._scrape_academic_content(source)
                else:
                    content = await self._scrape_web_content(source)  # Default to web scraping
                
                if content and len(content.get("text", "")) >= self.config["content_min_length"]:
                    # Process and analyze content
                    scraped_data = await self._process_scraped_content(source_id, source, content)
                    
                    if scraped_data.quality_score >= self.config["quality_threshold"]:
                        self.scraped_data[scraped_data.source_id] = scraped_data
                        
                        # Update source statistics
                        source.last_scraped = datetime.now()
                        source.success_rate = min(1.0, source.success_rate + 0.1)
                        
                        return True
                
                return False
                
            except Exception as e:
                self.logger.error(f"Error scraping {source.name}: {e}")
                source.success_rate = max(0.0, source.success_rate - 0.1)
                return False
    
    async def _scrape_web_content(self, source: DataSource) -> Dict[str, Any]:
        """Scrape content from web source"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                async with session.get(source.url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract title
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else "No Title"
                        
                        # Remove unwanted elements
                        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                            element.decompose()
                        
                        # Extract main content
                        content_text = soup.get_text(separator=' ', strip=True)
                        
                        return {
                            "title": title_text,
                            "text": content_text,
                            "url": source.url,
                            "status": "success"
                        }
                    else:
                        return {"status": "failed", "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _scrape_rss_feed(self, source: DataSource) -> Dict[str, Any]:
        """Scrape content from RSS feed"""
        try:
            feed = feedparser.parse(source.url)
            
            if feed.entries:
                # Get latest entry
                entry = feed.entries[0]
                
                title = entry.get('title', 'No Title')
                content = entry.get('description', '') or entry.get('summary', '')
                link = entry.get('link', source.url)
                
                return {
                    "title": title,
                    "text": content,
                    "url": link,
                    "status": "success"
                }
            else:
                return {"status": "failed", "error": "No feed entries"}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _scrape_api_data(self, source: DataSource) -> Dict[str, Any]:
        """Scrape data from API source"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract relevant information based on API structure
                        # This would need to be customized per API
                        
                        return {
                            "title": "API Data",
                            "text": json.dumps(data, indent=2),
                            "url": source.url,
                            "status": "success"
                        }
                    else:
                        return {"status": "failed", "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _scrape_academic_content(self, source: DataSource) -> Dict[str, Any]:
        """Scrape content from academic source"""
        # For academic sources, we might need special handling
        # For now, use web scraping with academic-specific extraction
        return await self._scrape_web_content(source)
    
    async def _process_scraped_content(self, source_id: str, source: DataSource, content: Dict[str, Any]) -> ScrapedData:
        """Process and analyze scraped content"""
        
        # Extract keywords using YAKE
        keywords = []
        if self.config["enable_nlp_analysis"]:
            try:
                kw_extractor = yake.KeywordExtractor(
                    lan="en",
                    n=3,
                    dedupLim=0.7,
                    top=10
                )
                
                keywords_scores = kw_extractor.extract_keywords(content["text"])
                keywords = [kw[1] for kw in keywords_scores]
                
            except Exception as e:
                self.logger.warning(f"Keyword extraction failed: {e}")
        
        # Analyze reading level
        reading_level = 0
        try:
            reading_level = int(flesch_reading_ease(content["text"]))
        except Exception as e:
            self.logger.warning(f"Reading level analysis failed: {e}")
        
        # Determine sentiment (simplified)
        sentiment = "neutral"
        positive_words = ["good", "great", "excellent", "amazing", "breakthrough", "innovative", "successful"]
        negative_words = ["bad", "poor", "terrible", "failed", "problem", "issue", "crisis"]
        
        text_lower = content["text"].lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(content, keywords, reading_level)
        
        # Create scraped data object
        scraped_data = ScrapedData(
            source_id=source_id,
            title=content["title"],
            content=content["text"][:2000],  # Limit content length
            url=content["url"],
            category=source.category,
            timestamp=datetime.now(),
            keywords=keywords,
            sentiment=sentiment,
            reading_level=reading_level,
            quality_score=quality_score,
            metadata={
                "source_name": source.name,
                "source_type": source.source_type,
                "content_length": len(content["text"]),
                "processing_time": datetime.now().isoformat()
            }
        )
        
        return scraped_data
    
    def _calculate_quality_score(self, content: Dict[str, Any], keywords: List[str], reading_level: int) -> float:
        """Calculate quality score for scraped content"""
        score = 0.0
        
        # Content length score (0-0.3)
        content_length = len(content["text"])
        if content_length > 1000:
            score += 0.3
        elif content_length > 500:
            score += 0.2
        elif content_length > 200:
            score += 0.1
        
        # Keywords score (0-0.3)
        if len(keywords) >= 5:
            score += 0.3
        elif len(keywords) >= 3:
            score += 0.2
        elif len(keywords) >= 1:
            score += 0.1
        
        # Title quality score (0-0.2)
        title = content.get("title", "")
        if len(title) > 10 and len(title) < 200:
            score += 0.2
        elif len(title) > 5:
            score += 0.1
        
        # Reading level score (0-0.2)
        if 30 <= reading_level <= 70:  # Good readability range
            score += 0.2
        elif 20 <= reading_level <= 80:
            score += 0.1
        
        return min(1.0, score)
    
    async def generate_research_prompts(self) -> Dict[str, Any]:
        """Generate 100 research prompts based on scraped data"""
        self.logger.info("Generating research prompts based on scraped data...")
        
        # Categorize data
        categorized_data = {}
        for data in self.scraped_data.values():
            if data.category not in categorized_data:
                categorized_data[data.category] = []
            categorized_data[data.category].append(data)
        
        # Generate prompts for each category
        prompt_templates = self._get_prompt_templates()
        generated_prompts = []
        
        for category, data_list in categorized_data.items():
            category_prompts = await self._generate_category_prompts(category, data_list, prompt_templates)
            generated_prompts.extend(category_prompts)
        
        # Ensure we have 100 prompts
        while len(generated_prompts) < 100:
            # Generate additional general prompts
            additional_prompts = await self._generate_general_prompts(len(generated_prompts))
            generated_prompts.extend(additional_prompts)
        
        # Limit to 100 prompts and prioritize
        generated_prompts = sorted(generated_prompts, key=lambda x: x.implementation_priority)[:100]
        
        # Store prompts
        for prompt in generated_prompts:
            self.research_prompts[prompt.prompt_id] = prompt
        
        self.stats["prompts_generated"] = len(generated_prompts)
        
        # Save prompts
        await self._save_research_prompts()
        
        self.logger.info(f"Generated {len(generated_prompts)} research prompts")
        
        return {
            "total_prompts": len(generated_prompts),
            "categories": list(categorized_data.keys()),
            "complexity_distribution": self._get_complexity_distribution(generated_prompts),
            "priority_distribution": self._get_priority_distribution(generated_prompts)
        }
    
    def _get_prompt_templates(self) -> Dict[str, List[str]]:
        """Get prompt templates for different categories"""
        return {
            "ai_research": [
                "How can we implement {concept} in our multi-agent system to enhance {capability}?",
                "What are the implications of {technology} for autonomous agent collaboration?",
                "Design an experiment to test {hypothesis} using our current AI infrastructure.",
                "How might {advancement} change the way agents process {data_type}?",
                "What ethical considerations should we address when implementing {ai_technique}?"
            ],
            "tech_innovation": [
                "How can we leverage {technology} to improve system performance by {percentage}%?",
                "What would be the impact of integrating {platform} into our ecosystem?",
                "Design a prototype that combines {tech1} and {tech2} for {use_case}.",
                "How can we optimize {process} using {emerging_technology}?",
                "What are the security implications of adopting {new_tech}?"
            ],
            "business_strategy": [
                "How can we monetize {capability} while maintaining {value}?",
                "What market opportunities exist for {application} in {industry}?",
                "Design a business model that scales {service} globally.",
                "How can we compete with {competitor} using {unique_advantage}?",
                "What partnership strategies would accelerate {objective}?"
            ],
            "development": [
                "How can we refactor {component} to support {new_requirement}?",
                "What testing strategy ensures {quality_metric} for {feature}?",
                "Design an API that enables {functionality} with {constraint}.",
                "How can we optimize {algorithm} for {performance_goal}?",
                "What deployment strategy minimizes {risk} while maximizing {benefit}?"
            ],
            "cybersecurity": [
                "How can we protect {asset} against {threat_type}?",
                "What security measures should we implement for {new_feature}?",
                "Design a threat detection system for {attack_vector}.",
                "How can we ensure {compliance_standard} while maintaining {functionality}?",
                "What incident response plan addresses {security_scenario}?"
            ]
        }
    
    async def _generate_category_prompts(self, category: str, data_list: List[ScrapedData], templates: Dict[str, List[str]]) -> List[ResearchPrompt]:
        """Generate prompts for a specific category"""
        prompts = []
        
        # Get relevant templates
        category_key = self._map_category_to_template(category)
        category_templates = templates.get(category_key, templates["tech_innovation"])
        
        # Extract key concepts from data
        all_keywords = []
        for data in data_list[:5]:  # Use top 5 data points
            all_keywords.extend(data.keywords)
        
        # Get most frequent keywords
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Generate prompts
        for i, template in enumerate(category_templates[:5]):  # Max 5 prompts per category
            try:
                # Fill template with relevant concepts
                concept = top_keywords[i % len(top_keywords)][0] if top_keywords else "emerging technology"
                
                prompt_text = template.format(
                    concept=concept,
                    technology=concept,
                    capability="system efficiency",
                    advancement=concept,
                    data_type="multi-modal data",
                    ai_technique=concept,
                    platform=concept,
                    percentage=random.randint(10, 50),
                    tech1=concept,
                    tech2=top_keywords[(i+1) % len(top_keywords)][0] if len(top_keywords) > 1 else "AI technology",
                    use_case="autonomous operations",
                    process="data processing",
                    emerging_technology=concept,
                    new_tech=concept
                )
                
                prompt_id = hashlib.md5(f"{category}_{i}_{prompt_text}".encode()).hexdigest()[:12]
                
                # Determine complexity
                complexity = "intermediate"
                if "design" in prompt_text.lower() or "experiment" in prompt_text.lower():
                    complexity = "advanced"
                elif "optimize" in prompt_text.lower() or "implement" in prompt_text.lower():
                    complexity = "expert"
                
                # Determine applications
                applications = self._determine_applications(category, prompt_text)
                
                # Determine impact
                impact = "medium"
                if "security" in prompt_text.lower() or "performance" in prompt_text.lower():
                    impact = "high"
                elif "optimize" in prompt_text.lower() or "scale" in prompt_text.lower():
                    impact = "critical"
                
                prompt = ResearchPrompt(
                    prompt_id=prompt_id,
                    title=f"{category.title()} Research: {concept.title()}",
                    prompt_text=prompt_text,
                    category=category,
                    complexity=complexity,
                    potential_applications=applications,
                    data_sources=[data.source_id for data in data_list[:3]],
                    estimated_impact=impact,
                    implementation_priority=self._calculate_priority(complexity, impact),
                    metadata={
                        "generated_from": category,
                        "keywords_used": [kw[0] for kw in top_keywords[:3]],
                        "generation_time": datetime.now().isoformat()
                    }
                )
                
                prompts.append(prompt)
                
            except Exception as e:
                self.logger.warning(f"Failed to generate prompt for {category}: {e}")
        
        return prompts
    
    async def _generate_general_prompts(self, start_index: int) -> List[ResearchPrompt]:
        """Generate general research prompts to fill quota"""
        general_prompts = [
            "How can we improve the overall system architecture for better scalability?",
            "What machine learning techniques could enhance agent decision-making?",
            "How can we implement better user experience across all interfaces?",
            "What security measures should be prioritized for the next version?",
            "How can we optimize resource utilization across all system components?",
            "What emerging technologies should we evaluate for future integration?",
            "How can we improve error handling and system resilience?",
            "What metrics should we implement for better system monitoring?",
            "How can we enhance inter-agent communication protocols?",
            "What automation opportunities exist in current manual processes?"
        ]
        
        prompts = []
        
        for i, prompt_text in enumerate(general_prompts):
            if start_index + i >= 100:
                break
                
            prompt_id = hashlib.md5(f"general_{i}_{prompt_text}".encode()).hexdigest()[:12]
            
            prompt = ResearchPrompt(
                prompt_id=prompt_id,
                title=f"General Research {start_index + i + 1}",
                prompt_text=prompt_text,
                category="general",
                complexity="intermediate",
                potential_applications=["system_improvement", "optimization", "enhancement"],
                data_sources=[],
                estimated_impact="medium",
                implementation_priority=50,
                metadata={
                    "type": "general_prompt",
                    "generation_time": datetime.now().isoformat()
                }
            )
            
            prompts.append(prompt)
        
        return prompts
    
    def _map_category_to_template(self, category: str) -> str:
        """Map data category to prompt template category"""
        mapping = {
            "ai_research": "ai_research",
            "ai_tools": "ai_research",
            "ai_education": "ai_research",
            "tech_news": "tech_innovation",
            "tech_research": "tech_innovation",
            "development": "development",
            "web_development": "development",
            "cybersecurity": "cybersecurity",
            "security_vulnerabilities": "cybersecurity",
            "business": "business_strategy",
            "innovation": "business_strategy",
            "market_intelligence": "business_strategy"
        }
        
        return mapping.get(category, "tech_innovation")
    
    def _determine_applications(self, category: str, prompt_text: str) -> List[str]:
        """Determine potential applications for a prompt"""
        applications = ["system_enhancement"]
        
        if "security" in prompt_text.lower():
            applications.append("security_improvement")
        if "performance" in prompt_text.lower():
            applications.append("performance_optimization")
        if "user" in prompt_text.lower():
            applications.append("user_experience")
        if "agent" in prompt_text.lower():
            applications.append("agent_enhancement")
        if "data" in prompt_text.lower():
            applications.append("data_processing")
        
        return applications
    
    def _calculate_priority(self, complexity: str, impact: str) -> int:
        """Calculate implementation priority"""
        complexity_score = {"basic": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        impact_score = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        
        # Higher impact and lower complexity = higher priority (lower number)
        priority = 50 - (impact_score.get(impact, 2) * 10) + (complexity_score.get(complexity, 2) * 5)
        
        return max(1, min(100, priority))
    
    def _get_complexity_distribution(self, prompts: List[ResearchPrompt]) -> Dict[str, int]:
        """Get distribution of prompt complexities"""
        distribution = {"basic": 0, "intermediate": 0, "advanced": 0, "expert": 0}
        
        for prompt in prompts:
            distribution[prompt.complexity] += 1
        
        return distribution
    
    def _get_priority_distribution(self, prompts: List[ResearchPrompt]) -> Dict[str, int]:
        """Get distribution of prompt priorities"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for prompt in prompts:
            if prompt.implementation_priority <= 25:
                distribution["high"] += 1
            elif prompt.implementation_priority <= 50:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution
    
    async def _save_scraped_data(self):
        """Save scraped data to file"""
        data_dir = Path("data/expansion")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        scraped_data_dict = {
            source_id: asdict(data) for source_id, data in self.scraped_data.items()
        }
        
        with open(data_dir / "scraped_data.json", 'w', encoding='utf-8') as f:
            json.dump(scraped_data_dict, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Saved {len(self.scraped_data)} scraped data entries")
    
    async def _save_research_prompts(self):
        """Save research prompts to file"""
        data_dir = Path("data/expansion")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        prompts_dict = {
            prompt_id: asdict(prompt) for prompt_id, prompt in self.research_prompts.items()
        }
        
        with open(data_dir / "research_prompts.json", 'w', encoding='utf-8') as f:
            json.dump(prompts_dict, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Saved {len(self.research_prompts)} research prompts")
    
    async def get_expansion_status(self) -> Dict[str, Any]:
        """Get comprehensive expansion status"""
        return {
            "engine_status": self.status,
            "version": self.version,
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "statistics": self.stats,
            "data_sources": {
                "total": len(self.data_sources),
                "categories": list(set([source.category for source in self.data_sources.values()])),
                "average_success_rate": sum([source.success_rate for source in self.data_sources.values()]) / len(self.data_sources) if self.data_sources else 0
            },
            "scraped_data": {
                "total_entries": len(self.scraped_data),
                "categories": list(set([data.category for data in self.scraped_data.values()])),
                "average_quality": sum([data.quality_score for data in self.scraped_data.values()]) / len(self.scraped_data) if self.scraped_data else 0
            },
            "research_prompts": {
                "total_prompts": len(self.research_prompts),
                "complexity_distribution": self._get_complexity_distribution(list(self.research_prompts.values())),
                "category_distribution": {category: len([p for p in self.research_prompts.values() if p.category == category]) 
                                       for category in set([p.category for p in self.research_prompts.values()])}
            },
            "last_update": datetime.now().isoformat()
        }

# Global instance
data_expansion_engine = DataExpansionEngine()

# Export for use by other modules
__all__ = ['DataExpansionEngine', 'data_expansion_engine', 'DataSource', 'ScrapedData', 'ResearchPrompt']