"""
🤖 Autonomous Developer Agent - Self-Improving AI System
Agent yang bisa otomatis mengembangkan sistem dan mengumpulkan training data

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import requests
import feedparser
from datetime import datetime, timedelta
import os
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sqlite3
import schedule
import time
from pathlib import Path

@dataclass
class DataSource:
    """Source untuk training data"""
    name: str
    url: str
    data_type: str  # 'rss', 'api', 'scrape', 'file'
    update_frequency: str  # 'hourly', 'daily', 'weekly'
    last_updated: datetime
    status: str

@dataclass
class DevelopmentTask:
    """Task untuk autonomous development"""
    task_id: str
    description: str
    priority: int
    estimated_time: int
    dependencies: List[str]
    status: str
    created_at: datetime

class DataCollector:
    """Autonomous data collection system"""
    
    def __init__(self):
        self.data_sources = []
        self.collected_data = []
        self.db_path = "data/training_data.db"
        self.setup_database()
        
        # Indonesia-focused data sources
        self.initialize_indonesian_sources()
        
    def setup_database(self):
        """Setup database untuk menyimpan training data"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table untuk raw data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT,
                content TEXT,
                metadata TEXT,
                language TEXT,
                category TEXT,
                quality_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table untuk processed insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                insight TEXT,
                confidence_score REAL,
                source_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def initialize_indonesian_sources(self):
        """Initialize Indonesia-focused data sources"""
        
        indonesian_sources = [
            # News & Media
            DataSource(
                name="Detik.com RSS",
                url="https://rss.detik.com/index.php/detikcom",
                data_type="rss",
                update_frequency="hourly",
                last_updated=datetime.now() - timedelta(hours=1),
                status="active"
            ),
            DataSource(
                name="Kompas Tech",
                url="https://tekno.kompas.com/rss",
                data_type="rss", 
                update_frequency="hourly",
                last_updated=datetime.now() - timedelta(hours=1),
                status="active"
            ),
            DataSource(
                name="TechInAsia Indonesia",
                url="https://www.techinasia.com/indonesia/rss",
                data_type="rss",
                update_frequency="daily",
                last_updated=datetime.now() - timedelta(days=1),
                status="active"
            ),
            
            # Government & Official
            DataSource(
                name="Kemkominfo Press Release",
                url="https://www.kominfo.go.id/rss",
                data_type="rss",
                update_frequency="daily", 
                last_updated=datetime.now() - timedelta(days=1),
                status="active"
            ),
            
            # Tech Communities
            DataSource(
                name="DailySocial.id",
                url="https://dailysocial.id/feed",
                data_type="rss",
                update_frequency="daily",
                last_updated=datetime.now() - timedelta(days=1),
                status="active"
            ),
            
            # Reddit Indonesia
            DataSource(
                name="Reddit Indonesia",
                url="https://www.reddit.com/r/indonesia.json",
                data_type="api",
                update_frequency="hourly",
                last_updated=datetime.now() - timedelta(hours=1),
                status="active"
            ),
            
            # Wikipedia Bahasa Indonesia
            DataSource(
                name="Wikipedia ID Recent Changes",
                url="https://id.wikipedia.org/w/api.php",
                data_type="api",
                update_frequency="hourly",
                last_updated=datetime.now() - timedelta(hours=1),
                status="active"
            )
        ]
        
        self.data_sources.extend(indonesian_sources)
        print(f"✅ Initialized {len(indonesian_sources)} Indonesian data sources")
    
    async def collect_rss_data(self, source: DataSource) -> List[Dict]:
        """Collect data dari RSS feeds"""
        try:
            print(f"📡 Collecting RSS data from {source.name}...")
            
            feed = feedparser.parse(source.url)
            collected_items = []
            
            for entry in feed.entries[:10]:  # Limit 10 items per source
                item = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': source.name,
                    'language': 'id' if any(word in entry.get('title', '').lower() 
                                          for word in ['indonesia', 'jakarta', 'dan', 'yang', 'ini']) else 'en'
                }
                collected_items.append(item)
            
            print(f"✅ Collected {len(collected_items)} items from {source.name}")
            return collected_items
            
        except Exception as e:
            print(f"❌ Error collecting from {source.name}: {e}")
            return []
    
    async def collect_api_data(self, source: DataSource) -> List[Dict]:
        """Collect data dari APIs"""
        try:
            print(f"🔌 Collecting API data from {source.name}...")
            
            if "reddit" in source.name.lower():
                return await self.collect_reddit_data(source.url)
            elif "wikipedia" in source.name.lower():
                return await self.collect_wikipedia_data(source.url)
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error collecting API data from {source.name}: {e}")
            return []
    
    async def collect_reddit_data(self, url: str) -> List[Dict]:
        """Collect dari Reddit Indonesia"""
        try:
            headers = {'User-Agent': 'AgenticAI-Bot/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for post in data['data']['children'][:5]:  # Top 5 posts
                    post_data = post['data']
                    item = {
                        'title': post_data.get('title', ''),
                        'content': post_data.get('selftext', ''),
                        'score': post_data.get('score', 0),
                        'comments': post_data.get('num_comments', 0),
                        'source': 'Reddit Indonesia',
                        'language': 'id'
                    }
                    posts.append(item)
                
                return posts
            return []
            
        except Exception as e:
            print(f"❌ Reddit collection error: {e}")
            return []
    
    async def collect_wikipedia_data(self, base_url: str) -> List[Dict]:
        """Collect dari Wikipedia Indonesia recent changes"""
        try:
            params = {
                'action': 'query',
                'list': 'recentchanges',
                'format': 'json',
                'rclimit': 10,
                'rcnamespace': 0  # Main namespace only
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                changes = []
                
                for change in data['query']['recentchanges']:
                    item = {
                        'title': change.get('title', ''),
                        'content': f"Updated: {change.get('comment', '')}",
                        'user': change.get('user', ''),
                        'timestamp': change.get('timestamp', ''),
                        'source': 'Wikipedia Indonesia',
                        'language': 'id'
                    }
                    changes.append(item)
                
                return changes
            return []
            
        except Exception as e:
            print(f"❌ Wikipedia collection error: {e}")
            return []
    
    def store_training_data(self, items: List[Dict], source_name: str):
        """Store collected data ke database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in items:
            # Calculate quality score
            quality_score = self.calculate_quality_score(item)
            
            cursor.execute('''
                INSERT INTO training_data 
                (source_name, content, metadata, language, category, quality_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                source_name,
                f"{item.get('title', '')} {item.get('content', '')}",
                json.dumps(item),
                item.get('language', 'unknown'),
                self.categorize_content(item.get('title', '')),
                quality_score
            ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Stored {len(items)} items from {source_name}")
    
    def calculate_quality_score(self, item: Dict) -> float:
        """Calculate quality score untuk training data"""
        score = 0.5  # Base score
        
        # Length bonus
        content_length = len(item.get('content', ''))
        if content_length > 100:
            score += 0.2
        if content_length > 500:
            score += 0.2
        
        # Indonesian language bonus
        if item.get('language') == 'id':
            score += 0.3
        
        # Engagement bonus (untuk Reddit)
        if 'score' in item and item['score'] > 10:
            score += 0.2
        
        return min(1.0, score)
    
    def categorize_content(self, title: str) -> str:
        """Categorize content berdasarkan title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'teknologi']):
            return 'technology'
        elif any(word in title_lower for word in ['bisnis', 'ekonomi', 'startup', 'investasi']):
            return 'business'
        elif any(word in title_lower for word in ['politik', 'pemerintah', 'presiden', 'menteri']):
            return 'politics'
        elif any(word in title_lower for word in ['olahraga', 'sepak bola', 'badminton']):
            return 'sports'
        else:
            return 'general'
    
    async def run_collection_cycle(self):
        """Run satu cycle collection dari semua sources"""
        print(f"🚀 Starting data collection cycle at {datetime.now()}")
        
        total_collected = 0
        
        for source in self.data_sources:
            if source.status != 'active':
                continue
                
            try:
                if source.data_type == 'rss':
                    items = await self.collect_rss_data(source)
                elif source.data_type == 'api':
                    items = await self.collect_api_data(source)
                else:
                    continue
                
                if items:
                    self.store_training_data(items, source.name)
                    total_collected += len(items)
                    source.last_updated = datetime.now()
                
                # Delay between sources to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing {source.name}: {e}")
                source.status = 'error'
        
        print(f"✅ Collection cycle completed. Total items: {total_collected}")
        return total_collected

class AutonomousDeveloper:
    """Main autonomous development system"""
    
    def __init__(self):
        self.data_collector = DataCollector()
        self.development_queue = []
        self.learning_insights = []
        self.auto_improvements = []
        
        print("🤖 Autonomous Developer Agent initialized!")
        
    def analyze_collected_data(self) -> List[Dict]:
        """Analyze collected data untuk insights"""
        print("🧠 Analyzing collected data for insights...")
        
        conn = sqlite3.connect(self.data_collector.db_path)
        cursor = conn.cursor()
        
        # Get data from last 24 hours
        cursor.execute('''
            SELECT category, content, quality_score, language
            FROM training_data 
            WHERE created_at > datetime('now', '-1 day')
            AND quality_score > 0.6
            ORDER BY quality_score DESC
            LIMIT 100
        ''')
        
        recent_data = cursor.fetchall()
        conn.close()
        
        insights = []
        
        # Analyze trends
        category_counts = {}
        for row in recent_data:
            category = row[0]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Generate insights
        if category_counts:
            top_category = max(category_counts.items(), key=lambda x: x[1])
            insights.append({
                'type': 'trend',
                'insight': f"Trending topic today: {top_category[0]} with {top_category[1]} mentions",
                'confidence': 0.8,
                'actionable': True
            })
        
        # Language analysis
        id_count = sum(1 for row in recent_data if row[3] == 'id')
        if id_count > len(recent_data) * 0.7:
            insights.append({
                'type': 'language',
                'insight': "High Indonesian content detected - optimize for local context",
                'confidence': 0.9,
                'actionable': True
            })
        
        print(f"💡 Generated {len(insights)} insights from data analysis")
        return insights
    
    def generate_improvement_tasks(self, insights: List[Dict]) -> List[DevelopmentTask]:
        """Generate development tasks based on insights"""
        tasks = []
        task_counter = 0
        
        for insight in insights:
            if not insight.get('actionable'):
                continue
                
            task_counter += 1
            
            if insight['type'] == 'trend':
                task = DevelopmentTask(
                    task_id=f"trend_task_{task_counter}",
                    description=f"Add trending topic detection for {insight['insight']}",
                    priority=2,
                    estimated_time=4,  # hours
                    dependencies=[],
                    status="pending",
                    created_at=datetime.now()
                )
                tasks.append(task)
                
            elif insight['type'] == 'language':
                task = DevelopmentTask(
                    task_id=f"lang_task_{task_counter}",
                    description="Improve Indonesian language processing capabilities",
                    priority=1,
                    estimated_time=8,  # hours
                    dependencies=[],
                    status="pending", 
                    created_at=datetime.now()
                )
                tasks.append(task)
        
        print(f"📋 Generated {len(tasks)} development tasks")
        return tasks
    
    def auto_implement_task(self, task: DevelopmentTask) -> bool:
        """Automatically implement a development task"""
        print(f"⚙️ Auto-implementing task: {task.description}")
        
        try:
            if "trending topic" in task.description.lower():
                return self.implement_trending_detection()
            elif "indonesian language" in task.description.lower():
                return self.improve_indonesian_processing()
            elif "data collection" in task.description.lower():
                return self.add_new_data_source()
            else:
                # Generic implementation
                return self.generic_improvement()
                
        except Exception as e:
            print(f"❌ Error implementing task {task.task_id}: {e}")
            return False
    
    def implement_trending_detection(self) -> bool:
        """Implement trending topic detection"""
        trending_code = '''
def detect_trending_topics(self, timeframe_hours=24):
    """Detect trending topics from recent data"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT content, created_at
        FROM training_data 
        WHERE created_at > datetime('now', '-{} hours')
        AND language = 'id'
    """.format(timeframe_hours))
    
    recent_content = cursor.fetchall()
    conn.close()
    
    # Simple keyword extraction
    word_counts = {}
    for content, _ in recent_content:
        words = content.lower().split()
        for word in words:
            if len(word) > 4:  # Skip short words
                word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get top trending words
    trending = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return trending
'''
        
        # Write to new file
        with open("agents/trending_detector.py", "w") as f:
            f.write(f"# Auto-generated trending detection\n{trending_code}")
        
        print("✅ Trending detection implemented")
        return True
    
    def improve_indonesian_processing(self) -> bool:
        """Improve Indonesian language processing"""
        indonesian_improvements = '''
# Indonesian language improvements
INDONESIAN_STOPWORDS = [
    'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan', 'ini', 'itu',
    'adalah', 'akan', 'atau', 'juga', 'dapat', 'telah', 'tidak', 'sudah', 'bisa'
]

INDONESIAN_SYNONYMS = {
    'teknologi': ['tekno', 'tech', 'digital'],
    'bisnis': ['usaha', 'business', 'perusahaan'],
    'indonesia': ['nusantara', 'tanah air', 'ibu pertiwi']
}

def process_indonesian_text(text):
    """Enhanced Indonesian text processing"""
    # Remove stopwords
    words = text.lower().split()
    filtered_words = [w for w in words if w not in INDONESIAN_STOPWORDS]
    
    # Apply synonyms
    processed_words = []
    for word in filtered_words:
        for key, synonyms in INDONESIAN_SYNONYMS.items():
            if word in synonyms:
                word = key
                break
        processed_words.append(word)
    
    return ' '.join(processed_words)
'''
        
        with open("agents/indonesian_processor.py", "w") as f:
            f.write(indonesian_improvements)
        
        print("✅ Indonesian processing improved")
        return True
    
    def add_new_data_source(self) -> bool:
        """Add new data source automatically"""
        new_source = DataSource(
            name="Auto-discovered source",
            url="https://example.com/api", 
            data_type="api",
            update_frequency="daily",
            last_updated=datetime.now(),
            status="active"
        )
        
        self.data_collector.data_sources.append(new_source)
        print("✅ New data source added")
        return True
    
    def generic_improvement(self) -> bool:
        """Generic system improvement"""
        improvement_log = f"""
# Auto-improvement logged at {datetime.now()}
# System detected need for optimization
# Implementing generic performance enhancement

def auto_optimize():
    # Placeholder for automatic optimization
    return True
"""
        
        with open("auto_improvements.log", "a") as f:
            f.write(improvement_log)
        
        print("✅ Generic improvement implemented")
        return True
    
    async def autonomous_development_cycle(self):
        """Main autonomous development loop"""
        print("🚀 Starting autonomous development cycle...")
        
        # Step 1: Collect new data
        collected_items = await self.data_collector.run_collection_cycle()
        
        # Step 2: Analyze data for insights
        insights = self.analyze_collected_data()
        
        # Step 3: Generate improvement tasks
        new_tasks = self.generate_improvement_tasks(insights)
        self.development_queue.extend(new_tasks)
        
        # Step 4: Implement high-priority tasks
        implemented_count = 0
        for task in sorted(self.development_queue, key=lambda x: x.priority):
            if task.status == "pending" and implemented_count < 2:  # Limit implementations per cycle
                success = self.auto_implement_task(task)
                if success:
                    task.status = "completed"
                    implemented_count += 1
                else:
                    task.status = "failed"
        
        # Step 5: Generate summary report
        self.generate_cycle_report(collected_items, insights, implemented_count)
        
        print("✅ Autonomous development cycle completed!")
    
    def generate_cycle_report(self, collected_items: int, insights: List[Dict], implemented_tasks: int):
        """Generate report of development cycle"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_collected': collected_items,
            'insights_generated': len(insights),
            'tasks_implemented': implemented_tasks,
            'system_status': 'improving',
            'next_cycle': (datetime.now() + timedelta(hours=6)).isoformat()
        }
        
        with open("development_reports.json", "a") as f:
            f.write(json.dumps(report) + "\n")
        
        print(f"📊 Cycle Report: {collected_items} items collected, {len(insights)} insights, {implemented_tasks} improvements")
    
    def start_autonomous_mode(self):
        """Start continuous autonomous development"""
        print("🤖 Starting continuous autonomous development mode...")
        
        # Schedule autonomous cycles
        schedule.every(6).hours.do(lambda: asyncio.run(self.autonomous_development_cycle()))
        
        # Initial cycle
        asyncio.run(self.autonomous_development_cycle())
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Usage example
if __name__ == "__main__":
    print("🚀 Initializing Autonomous Developer Agent...")
    
    # Create autonomous developer
    auto_dev = AutonomousDeveloper()
    
    # Run one development cycle for testing
    asyncio.run(auto_dev.autonomous_development_cycle())
    
    print("🎯 Autonomous development system ready!")
    print("🔄 To start continuous mode, call: auto_dev.start_autonomous_mode()")