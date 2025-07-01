"""
🔄 Data Augmentation System - Smart Training Data Multiplier
Sistem untuk menggandakan dan memperkaya training data secara otomatis

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import json
import random
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio
import requests
from dataclasses import dataclass

@dataclass
class AugmentationRule:
    """Rule untuk data augmentation"""
    rule_id: str
    name: str
    input_type: str
    output_multiplier: int
    quality_boost: float
    enabled: bool

class IndonesianDataAugmenter:
    """Advanced Indonesian data augmentation"""
    
    def __init__(self):
        self.synonyms = {
            # Technology terms
            'artificial intelligence': ['kecerdasan buatan', 'AI', 'machine learning', 'teknologi pintar'],
            'teknologi': ['technology', 'tech', 'digital', 'inovasi'],
            'startup': ['perusahaan rintisan', 'bisnis baru', 'usaha teknologi'],
            'aplikasi': ['app', 'software', 'program', 'platform'],
            
            # Business terms  
            'bisnis': ['business', 'usaha', 'perusahaan', 'commerce'],
            'investasi': ['investment', 'modal', 'funding', 'dana'],
            'ekonomi': ['economy', 'financial', 'keuangan'],
            'pasar': ['market', 'marketplace', 'perdagangan'],
            
            # Indonesian specific
            'indonesia': ['nusantara', 'tanah air', 'republik indonesia', 'RI'],
            'jakarta': ['DKI Jakarta', 'ibukota', 'metropolitan'],
            'pemerintah': ['government', 'negara', 'publik', 'nasional']
        }
        
        self.sentence_templates = [
            "Dalam konteks {topic}, {subject} menjadi {importance} untuk {goal}",
            "Menurut {source}, {statement} akan {impact} terhadap {sector}",
            "Perkembangan {field} di Indonesia menunjukkan {trend} yang {evaluation}",
            "Para ahli memprediksi bahwa {prediction} akan {result} dalam {timeframe}",
            "Dengan adanya {innovation}, {benefit} dapat {achievement} secara {manner}"
        ]
        
        self.context_expanders = {
            'teknologi': ['digital transformation', 'Industry 4.0', 'smart city', 'IoT'],
            'bisnis': ['e-commerce', 'digital marketing', 'fintech', 'startup ecosystem'],
            'pendidikan': ['online learning', 'EdTech', 'digital literacy', 'skill development'],
            'kesehatan': ['telemedicine', 'health tech', 'digital health', 'medical AI']
        }
        
    def augment_text_synonyms(self, text: str) -> List[str]:
        """Augment text menggunakan synonyms"""
        variations = [text]  # Original text
        
        for original, synonyms in self.synonyms.items():
            if original.lower() in text.lower():
                for synonym in synonyms:
                    new_text = text.replace(original, synonym)
                    if new_text != text:
                        variations.append(new_text)
        
        return variations[:5]  # Limit to 5 variations
    
    def augment_with_context(self, title: str, content: str) -> List[Dict[str, str]]:
        """Add contextual information to expand content"""
        augmented_items = []
        
        # Detect main topic
        topic = self.detect_topic(title + " " + content)
        
        if topic and topic in self.context_expanders:
            related_terms = self.context_expanders[topic]
            
            for term in related_terms[:3]:  # Use top 3 related terms
                expanded_content = f"{content}\n\nDalam konteks {term}, topik ini juga relevan dengan perkembangan {topic} di Indonesia."
                
                augmented_items.append({
                    'title': f"{title} - Perspektif {term}",
                    'content': expanded_content,
                    'augmentation_type': 'context_expansion',
                    'original_topic': topic
                })
        
        return augmented_items
    
    def detect_topic(self, text: str) -> Optional[str]:
        """Detect main topic from text"""
        text_lower = text.lower()
        
        topic_keywords = {
            'teknologi': ['ai', 'artificial intelligence', 'teknologi', 'digital', 'software', 'app'],
            'bisnis': ['bisnis', 'startup', 'investasi', 'ekonomi', 'pasar', 'commerce'],
            'pendidikan': ['pendidikan', 'sekolah', 'universitas', 'belajar', 'mahasiswa'],
            'kesehatan': ['kesehatan', 'medis', 'rumah sakit', 'dokter', 'pengobatan']
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        return None
    
    def generate_questions_answers(self, title: str, content: str) -> List[Dict[str, str]]:
        """Generate Q&A pairs from content"""
        qa_pairs = []
        
        # Simple question templates
        question_templates = [
            f"Apa yang dimaksud dengan {title}?",
            f"Bagaimana {title} mempengaruhi Indonesia?",
            f"Mengapa {title} penting untuk dipahami?",
            f"Kapan {title} mulai berkembang?",
            f"Siapa yang terlibat dalam {title}?"
        ]
        
        for question in question_templates[:3]:  # Generate 3 questions
            answer = f"Berdasarkan informasi yang tersedia: {content[:200]}..."
            
            qa_pairs.append({
                'title': question,
                'content': answer,
                'augmentation_type': 'question_answer',
                'original_title': title
            })
        
        return qa_pairs

class DataMultiplier:
    """System untuk menggandakan training data"""
    
    def __init__(self, db_path: str = "data/training_data.db"):
        self.db_path = db_path
        self.augmenter = IndonesianDataAugmenter()
        
        self.augmentation_rules = [
            AugmentationRule(
                rule_id="synonyms",
                name="Synonym Replacement",
                input_type="text",
                output_multiplier=3,
                quality_boost=0.8,
                enabled=True
            ),
            AugmentationRule(
                rule_id="context_expansion",
                name="Context Expansion",
                input_type="text",
                output_multiplier=2,
                quality_boost=0.9,
                enabled=True
            ),
            AugmentationRule(
                rule_id="qa_generation",
                name="Q&A Generation",
                input_type="text",
                output_multiplier=3,
                quality_boost=0.7,
                enabled=True
            ),
            AugmentationRule(
                rule_id="paraphrasing",
                name="Intelligent Paraphrasing",
                input_type="text",
                output_multiplier=2,
                quality_boost=0.85,
                enabled=True
            )
        ]
    
    def get_original_data(self, limit: int = 100) -> List[Dict]:
        """Get original data for augmentation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, source_name, content, language, category, quality_score
            FROM training_data 
            WHERE quality_score > 0.6
            AND language = 'id'
            ORDER BY quality_score DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        data_items = []
        for row in rows:
            item = {
                'id': row[0],
                'source_name': row[1],
                'content': row[2],
                'language': row[3],
                'category': row[4],
                'quality_score': row[5]
            }
            data_items.append(item)
        
        return data_items
    
    def augment_single_item(self, item: Dict) -> List[Dict]:
        """Augment single data item"""
        augmented_items = []
        content = item['content']
        
        # Split content to title and body
        parts = content.split(' ', 10)
        title = ' '.join(parts[:5]) if len(parts) > 5 else content[:50]
        body = ' '.join(parts[5:]) if len(parts) > 5 else content[50:]
        
        # Apply augmentation rules
        for rule in self.augmentation_rules:
            if not rule.enabled:
                continue
                
            try:
                if rule.rule_id == "synonyms":
                    variations = self.augmenter.augment_text_synonyms(content)
                    for variation in variations[1:]:  # Skip original
                        augmented_items.append({
                            'original_id': item['id'],
                            'title': title,
                            'content': variation,
                            'source_name': f"{item['source_name']} - Augmented",
                            'language': item['language'],
                            'category': item['category'],
                            'quality_score': item['quality_score'] * rule.quality_boost,
                            'augmentation_type': rule.rule_id,
                            'created_at': datetime.now()
                        })
                
                elif rule.rule_id == "context_expansion":
                    expanded_items = self.augmenter.augment_with_context(title, body)
                    for expanded in expanded_items:
                        augmented_items.append({
                            'original_id': item['id'],
                            'title': expanded['title'],
                            'content': expanded['content'],
                            'source_name': f"{item['source_name']} - Context Expanded",
                            'language': item['language'],
                            'category': item['category'],
                            'quality_score': item['quality_score'] * rule.quality_boost,
                            'augmentation_type': rule.rule_id,
                            'created_at': datetime.now()
                        })
                
                elif rule.rule_id == "qa_generation":
                    qa_pairs = self.augmenter.generate_questions_answers(title, body)
                    for qa in qa_pairs:
                        augmented_items.append({
                            'original_id': item['id'],
                            'title': qa['title'],
                            'content': qa['content'],
                            'source_name': f"{item['source_name']} - Q&A",
                            'language': item['language'],
                            'category': item['category'],
                            'quality_score': item['quality_score'] * rule.quality_boost,
                            'augmentation_type': rule.rule_id,
                            'created_at': datetime.now()
                        })
                
                elif rule.rule_id == "paraphrasing":
                    paraphrased = self.intelligent_paraphrase(content)
                    if paraphrased:
                        augmented_items.append({
                            'original_id': item['id'],
                            'title': title,
                            'content': paraphrased,
                            'source_name': f"{item['source_name']} - Paraphrased",
                            'language': item['language'],
                            'category': item['category'],
                            'quality_score': item['quality_score'] * rule.quality_boost,
                            'augmentation_type': rule.rule_id,
                            'created_at': datetime.now()
                        })
                        
            except Exception as e:
                print(f"❌ Error in augmentation rule {rule.rule_id}: {e}")
                continue
        
        return augmented_items
    
    def intelligent_paraphrase(self, text: str) -> Optional[str]:
        """Intelligent paraphrasing using templates"""
        
        # Simple paraphrasing patterns
        paraphrase_patterns = [
            ("adalah", "merupakan"),
            ("sangat penting", "memiliki peran vital"),
            ("berkembang pesat", "mengalami pertumbuhan signifikan"),
            ("di Indonesia", "dalam konteks Indonesia"),
            ("masa depan", "prospek ke depan"),
            ("teknologi baru", "inovasi teknologi"),
            ("memberikan manfaat", "menyediakan keunggulan")
        ]
        
        paraphrased = text
        replacements_made = 0
        
        for original, replacement in paraphrase_patterns:
            if original in paraphrased.lower() and replacements_made < 3:
                paraphrased = paraphrased.replace(original, replacement)
                replacements_made += 1
        
        return paraphrased if replacements_made > 0 else None
    
    def store_augmented_data(self, augmented_items: List[Dict]):
        """Store augmented data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create augmented data table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS augmented_training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_id INTEGER,
                source_name TEXT,
                content TEXT,
                metadata TEXT,
                language TEXT,
                category TEXT,
                quality_score REAL,
                augmentation_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (original_id) REFERENCES training_data (id)
            )
        ''')
        
        for item in augmented_items:
            cursor.execute('''
                INSERT INTO augmented_training_data 
                (original_id, source_name, content, metadata, language, category, quality_score, augmentation_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['original_id'],
                item['source_name'],
                f"{item['title']} {item['content']}",
                json.dumps({k: v for k, v in item.items() if k not in ['original_id', 'source_name', 'content']}),
                item['language'],
                item['category'],
                item['quality_score'],
                item['augmentation_type']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Stored {len(augmented_items)} augmented data items")
    
    async def run_augmentation_cycle(self, batch_size: int = 50) -> Dict[str, int]:
        """Run complete augmentation cycle"""
        print(f"🔄 Starting data augmentation cycle...")
        
        # Get original data
        original_data = self.get_original_data(batch_size)
        print(f"📊 Processing {len(original_data)} original items")
        
        # Augment each item
        all_augmented = []
        for item in original_data:
            augmented = self.augment_single_item(item)
            all_augmented.extend(augmented)
            
            # Progress indicator
            if len(all_augmented) % 100 == 0:
                print(f"🔄 Processed {len(all_augmented)} augmented items...")
        
        # Store augmented data
        if all_augmented:
            self.store_augmented_data(all_augmented)
        
        # Calculate statistics
        stats = {
            'original_items': len(original_data),
            'augmented_items': len(all_augmented),
            'multiplier_ratio': len(all_augmented) / len(original_data) if original_data else 0,
            'augmentation_types': {}
        }
        
        # Count by augmentation type
        for item in all_augmented:
            aug_type = item['augmentation_type']
            stats['augmentation_types'][aug_type] = stats['augmentation_types'].get(aug_type, 0) + 1
        
        print(f"✅ Augmentation completed: {len(original_data)} → {len(all_augmented)} items")
        return stats

class SmartDataGenerator:
    """Generate entirely new training data from patterns"""
    
    def __init__(self):
        self.indonesian_topics = [
            "Perkembangan AI di Indonesia",
            "Startup teknologi Jakarta", 
            "Digital transformation UMKM",
            "Fintech dan ekonomi digital",
            "E-commerce Indonesia",
            "Pendidikan online Indonesia",
            "Smart city Jakarta",
            "Teknologi blockchain Indonesia",
            "Cybersecurity awareness",
            "Data privacy Indonesia"
        ]
        
        self.content_templates = [
            "Indonesia mengalami pertumbuhan {topic} yang sangat pesat dalam {timeframe}. Hal ini didorong oleh {factors} dan dukungan dari {supporters}. Dampaknya terhadap {impact_area} sangat signifikan dan diharapkan akan {future_expectation}.",
            
            "Dalam konteks {topic}, Indonesia memiliki potensi besar untuk {opportunity}. Tantangan yang dihadapi meliputi {challenges}, namun dengan {solutions} yang tepat, masa depan {topic} di Indonesia terlihat cerah.",
            
            "Para ahli memprediksi bahwa {topic} akan mengubah landscape {industry} Indonesia dalam {timeframe}. Investasi dalam {investment_area} menjadi kunci untuk {success_metric}."
        ]
        
    def generate_synthetic_content(self, count: int = 20) -> List[Dict]:
        """Generate synthetic Indonesian content"""
        generated_items = []
        
        for i in range(count):
            topic = random.choice(self.indonesian_topics)
            template = random.choice(self.content_templates)
            
            # Fill template with contextual information
            filled_content = template.format(
                topic=topic.lower(),
                timeframe=random.choice(["3 tahun terakhir", "dekade ini", "5 tahun ke depan"]),
                factors=random.choice(["investasi asing", "talent lokal", "dukungan pemerintah", "inovasi startup"]),
                supporters=random.choice(["pemerintah", "sektor swasta", "universitas", "komunitas tech"]),
                impact_area=random.choice(["ekonomi digital", "masyarakat", "industri", "pendidikan"]),
                future_expectation=random.choice(["menjadi regional leader", "menciptakan lapangan kerja", "meningkatkan produktivitas"]),
                opportunity=random.choice(["memimpin di ASEAN", "menjadi unicorn", "go international"]),
                challenges=random.choice(["infrastruktur", "regulasi", "talent gap", "akses modal"]),
                solutions=random.choice(["kolaborasi publik-swasta", "program training", "reformasi regulasi"]),
                industry=random.choice(["teknologi", "finansial", "e-commerce", "pendidikan"]),
                investment_area=random.choice(["R&D", "infrastruktur", "human capital", "teknologi"]),
                success_metric=random.choice(["mencapai target nasional", "bersaing global", "sustainable growth"])
            )
            
            generated_items.append({
                'title': topic,
                'content': filled_content,
                'source_name': 'AI Generated - Synthetic',
                'language': 'id',
                'category': 'technology',
                'quality_score': 0.75,
                'generation_type': 'synthetic_template',
                'created_at': datetime.now()
            })
        
        return generated_items

# Main augmentation system
class ComprehensiveDataAugmenter:
    """Complete data augmentation and generation system"""
    
    def __init__(self, db_path: str = "data/training_data.db"):
        self.multiplier = DataMultiplier(db_path)
        self.generator = SmartDataGenerator()
        
    async def massive_data_expansion(self, target_items: int = 10000) -> Dict[str, Any]:
        """Massively expand training data to reach target"""
        print(f"🚀 Starting massive data expansion to {target_items} items...")
        
        # Current data count
        conn = sqlite3.connect(self.multiplier.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM training_data")
        current_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"📊 Current data: {current_count} items, Target: {target_items}")
        
        expansion_stats = {
            'starting_count': current_count,
            'target_count': target_items,
            'augmentation_stats': {},
            'generation_stats': {},
            'final_count': 0
        }
        
        items_needed = target_items - current_count
        
        if items_needed > 0:
            # Phase 1: Augment existing data
            print("🔄 Phase 1: Augmenting existing data...")
            aug_stats = await self.multiplier.run_augmentation_cycle(batch_size=min(500, current_count))
            expansion_stats['augmentation_stats'] = aug_stats
            
            # Phase 2: Generate synthetic data if still needed
            remaining_needed = items_needed - aug_stats['augmented_items']
            if remaining_needed > 0:
                print(f"🎭 Phase 2: Generating {remaining_needed} synthetic items...")
                
                # Generate in batches
                synthetic_items = []
                batches = (remaining_needed // 100) + 1
                
                for batch in range(min(batches, 50)):  # Max 50 batches
                    batch_items = self.generator.generate_synthetic_content(
                        count=min(100, remaining_needed - len(synthetic_items))
                    )
                    synthetic_items.extend(batch_items)
                    
                    if len(synthetic_items) >= remaining_needed:
                        break
                
                # Store synthetic data
                if synthetic_items:
                    self.store_synthetic_data(synthetic_items)
                
                expansion_stats['generation_stats'] = {
                    'synthetic_items': len(synthetic_items),
                    'batches_generated': len(synthetic_items) // 100 + 1
                }
        
        # Final count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM training_data")
        cursor.execute("SELECT COUNT(*) FROM augmented_training_data") 
        final_original = cursor.fetchone()[0]
        final_augmented = cursor.fetchone()[0] if cursor.fetchone() else 0
        conn.close()
        
        expansion_stats['final_count'] = final_original + final_augmented
        
        print(f"✅ Data expansion completed!")
        print(f"📈 Final count: {expansion_stats['final_count']} items")
        
        return expansion_stats
    
    def store_synthetic_data(self, synthetic_items: List[Dict]):
        """Store synthetic data in main training table"""
        conn = sqlite3.connect(self.multiplier.db_path)
        cursor = conn.cursor()
        
        for item in synthetic_items:
            cursor.execute('''
                INSERT INTO training_data 
                (source_name, content, metadata, language, category, quality_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item['source_name'],
                f"{item['title']} {item['content']}",
                json.dumps(item),
                item['language'],
                item['category'],
                item['quality_score']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Stored {len(synthetic_items)} synthetic data items")

# Usage example
if __name__ == "__main__":
    print("🔄 Initializing Data Augmentation System...")
    
    # Create comprehensive augmenter
    augmenter = ComprehensiveDataAugmenter()
    
    # Run massive expansion
    asyncio.run(augmenter.massive_data_expansion(target_items=5000))
    
    print("🎯 Data augmentation system ready!")
    print("🚀 Your AI now has Google-level data quantity!")