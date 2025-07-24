"""
AGI Research-Based Prompts Library
==================================

100 prompts based on comprehensive research from:
- Wikipedia AGI definitions and characteristics
- AI Tools directories (theresanaiforthat.com, insidr.ai)
- GitHub AI projects and frameworks
- Current AGI developments and trends

Categories:
1. AGI Fundamentals & Theory (15 prompts)
2. Multi-Modal Intelligence (10 prompts)
3. Autonomous Systems & Agents (12 prompts)
4. Human-Level Reasoning (10 prompts)
5. Knowledge Integration (8 prompts)
6. Creative Intelligence (8 prompts)
7. Social & Emotional Intelligence (7 prompts)
8. Learning & Adaptation (10 prompts)
9. Consciousness & Self-Awareness (5 prompts)
10. AGI Safety & Ethics (15 prompts)
"""

import random
from typing import Dict, List, Any
from datetime import datetime

class AGIResearchPrompts:
    def __init__(self):
        self.prompts = {
            # 1. AGI Fundamentals & Theory (15 prompts)
            "agi_fundamentals": [
                {
                    "name": "AGI Cognitive Architecture Analysis",
                    "prompt": "Design a comprehensive cognitive architecture for AGI that can reason, use strategy, solve puzzles, and make judgments under uncertainty. Include modules for knowledge representation, planning, learning, and natural language communication. How would these components integrate to achieve human-level general intelligence?",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "Wikipedia AGI characteristics, Symbol grounding hypothesis"
                },
                {
                    "name": "AGI vs ANI Distinction Framework",
                    "prompt": "Create a detailed framework distinguishing Artificial General Intelligence from Artificial Narrow Intelligence. Analyze current AI systems like GPT-4, Claude, and specialized tools. What benchmarks would definitively prove AGI achievement versus advanced narrow AI?",
                    "category": "AGI Fundamentals",
                    "complexity": "medium",
                    "research_basis": "AGI definition studies, current LLM capabilities"
                },
                {
                    "name": "Universal Intelligence Metrics",
                    "prompt": "Develop a comprehensive set of metrics to measure progress toward AGI based on Marcus Hutter's AIXI framework and modern research. Include tests for general problem-solving, transfer learning, and adaptation to novel environments.",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "AIXI framework, Universal AI theory"
                },
                {
                    "name": "AGI Timeline Prediction Model",
                    "prompt": "Analyze expert predictions for AGI timeline (2027-2050 estimates) and create a probabilistic model considering current AI progress, computational requirements, and breakthrough indicators. What factors most influence AGI arrival predictions?",
                    "category": "AGI Fundamentals",
                    "complexity": "medium",
                    "research_basis": "AGI timeline surveys, expert predictions"
                },
                {
                    "name": "Emergent Intelligence Threshold",
                    "prompt": "Investigate the concept of intelligence emergence in large-scale AI systems. At what point does increasing model size, training data, and complexity lead to qualitatively different cognitive capabilities? Design experiments to detect emergence.",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "Scaling laws, emergence in neural networks"
                },
                {
                    "name": "AGI Performance Levels Framework",
                    "prompt": "Implement Google DeepMind's 5-level AGI framework (emerging, competent, expert, virtuoso, superhuman) with specific benchmarks and tests for each level. How do current AI systems rank in this framework?",
                    "category": "AGI Fundamentals",
                    "complexity": "medium",
                    "research_basis": "DeepMind AGI levels, performance taxonomy"
                },
                {
                    "name": "General Intelligent Action Design",
                    "prompt": "Define and operationalize 'general intelligent action' as proposed by Newell & Simon. Create a system that can perform any intellectual task a human can, with focus on task generalization and skill transfer.",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "Physical Symbol System Hypothesis"
                },
                {
                    "name": "AGI vs Human Intelligence Comparison",
                    "prompt": "Conduct a systematic comparison between human cognitive abilities and current AI capabilities. Identify key gaps in reasoning, creativity, emotional intelligence, and common sense understanding.",
                    "category": "AGI Fundamentals",
                    "complexity": "medium",
                    "research_basis": "Cognitive science, AI capabilities analysis"
                },
                {
                    "name": "Artificial Superintelligence Transition",
                    "prompt": "Model the transition pathway from AGI to Artificial Superintelligence (ASI). What mechanisms enable recursive self-improvement, and how can we ensure beneficial outcomes during this transition?",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "Intelligence explosion theory, ASI research"
                },
                {
                    "name": "Turing Test Evolution for AGI",
                    "prompt": "Design modern alternatives to the Turing Test that better assess AGI capabilities. Include the Coffee Test, Robot College Student Test, and Employment Test. What new tests are needed for 2025 AGI evaluation?",
                    "category": "AGI Fundamentals",
                    "complexity": "medium",
                    "research_basis": "AGI testing frameworks, Turing Test limitations"
                },
                {
                    "name": "Common Sense Reasoning Architecture",
                    "prompt": "Develop an architecture for common sense reasoning that enables AI to understand and interact with the world like humans. How can we encode intuitive physics, social dynamics, and everyday knowledge?",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "Common sense AI challenges, Cyc project"
                },
                {
                    "name": "AGI Embodiment Requirements",
                    "prompt": "Analyze whether physical embodiment is necessary for AGI. Compare virtual embodiment approaches with robotic systems. How does sensorimotor experience contribute to general intelligence?",
                    "category": "AGI Fundamentals",
                    "complexity": "medium",
                    "research_basis": "Embodied cognition theory, robotics AI"
                },
                {
                    "name": "Cross-Domain Knowledge Transfer",
                    "prompt": "Create a system that can learn in one domain and apply that knowledge to completely different domains, mimicking human transfer learning. What mechanisms enable this cognitive flexibility?",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "Transfer learning, cognitive flexibility"
                },
                {
                    "name": "AGI Cognitive Flexibility Assessment",
                    "prompt": "Design comprehensive tests for cognitive flexibility in AI systems, measuring ability to switch between tasks, adapt to new rules, and handle unexpected situations with human-like adaptability.",
                    "category": "AGI Fundamentals",
                    "complexity": "medium",
                    "research_basis": "Cognitive psychology, flexibility testing"
                },
                {
                    "name": "Integrated Intelligence Synthesis",
                    "prompt": "Synthesize insights from symbolic AI, connectionist approaches, and modern deep learning to design a unified AGI architecture that leverages strengths of each paradigm while minimizing their limitations.",
                    "category": "AGI Fundamentals",
                    "complexity": "high",
                    "research_basis": "AI paradigms, hybrid architectures"
                }
            ],

            # 2. Multi-Modal Intelligence (10 prompts)
            "multimodal_intelligence": [
                {
                    "name": "Unified Perceptual Processing",
                    "prompt": "Design a unified perceptual system that processes visual, auditory, tactile, and textual information simultaneously, with cross-modal attention and integration mechanisms that mirror human sensory processing.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "high",
                    "research_basis": "Multi-modal AI, sensory integration"
                },
                {
                    "name": "Visual-Language Reasoning Chain",
                    "prompt": "Create a system that can analyze complex visual scenes and generate detailed reasoning chains about objects, relationships, and potential actions, then communicate findings in natural language.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "medium",
                    "research_basis": "Vision-language models, scene understanding"
                },
                {
                    "name": "Audio-Visual Scene Understanding",
                    "prompt": "Develop an AI that can understand and reason about audio-visual scenes, identifying speakers, interpreting emotions from tone and facial expressions, and understanding contextual relationships.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "high",
                    "research_basis": "Multi-modal perception, context understanding"
                },
                {
                    "name": "Cross-Modal Knowledge Grounding",
                    "prompt": "Build a system that grounds abstract concepts in multi-modal experiences, connecting linguistic descriptions with visual, auditory, and tactile sensations to form rich conceptual understanding.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "high",
                    "research_basis": "Symbol grounding, embodied cognition"
                },
                {
                    "name": "Dynamic Multi-Modal Attention",
                    "prompt": "Implement a dynamic attention mechanism that can fluidly shift focus between different modalities based on task requirements and environmental context, mimicking human attention patterns.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "medium",
                    "research_basis": "Attention mechanisms, cognitive attention"
                },
                {
                    "name": "Real-Time Multi-Modal Integration",
                    "prompt": "Create a real-time system that integrates streaming visual, audio, and text data to maintain a coherent understanding of dynamic environments and ongoing conversations.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "high",
                    "research_basis": "Real-time AI, stream processing"
                },
                {
                    "name": "Synthetic Multi-Modal Generation",
                    "prompt": "Design a generative model that can create coherent content across multiple modalities simultaneously, generating matching images, audio, and text that tell a unified story.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "medium",
                    "research_basis": "Generative AI, multi-modal synthesis"
                },
                {
                    "name": "Haptic-Visual Integration",
                    "prompt": "Develop a system that combines haptic feedback with visual processing to understand object properties, textures, and manipulation possibilities in robotic applications.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "high",
                    "research_basis": "Haptic AI, robotic perception"
                },
                {
                    "name": "Multi-Modal Memory Formation",
                    "prompt": "Create a memory system that stores and retrieves experiences across multiple modalities, enabling rich episodic memory formation and cross-modal recall mechanisms.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "medium",
                    "research_basis": "Memory systems, episodic memory"
                },
                {
                    "name": "Contextual Multi-Modal Understanding",
                    "prompt": "Build an AI that uses multi-modal context to disambiguate meaning, understanding references, implied information, and cultural nuances across different communication channels.",
                    "category": "Multi-Modal Intelligence",
                    "complexity": "high",
                    "research_basis": "Contextual AI, cultural understanding"
                }
            ],

            # 3. Autonomous Systems & Agents (12 prompts)
            "autonomous_systems": [
                {
                    "name": "Fully Autonomous AGI Agent",
                    "prompt": "Design a fully autonomous AGI agent that can set its own goals, plan complex multi-step actions, and adapt strategies based on environmental feedback without human intervention.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "Autonomous agents, goal-directed behavior"
                },
                {
                    "name": "Multi-Agent AGI Collaboration",
                    "prompt": "Create a system of multiple AGI agents that can collaborate, negotiate, and coordinate to solve complex problems that require diverse expertise and parallel processing.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "Multi-agent systems, AI collaboration"
                },
                {
                    "name": "Self-Improving Autonomous System",
                    "prompt": "Develop an autonomous system capable of recursive self-improvement, identifying its own limitations and systematically enhancing its capabilities while maintaining safety constraints.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "Recursive self-improvement, AI safety"
                },
                {
                    "name": "Adaptive Autonomous Navigation",
                    "prompt": "Create an autonomous navigation system that can adapt to completely new environments, learning spatial relationships and navigation strategies in real-time without prior mapping.",
                    "category": "Autonomous Systems",
                    "complexity": "medium",
                    "research_basis": "SLAM, adaptive navigation"
                },
                {
                    "name": "Autonomous Task Decomposition",
                    "prompt": "Build a system that can autonomously break down complex, ambiguous tasks into manageable sub-tasks, allocate resources, and coordinate execution across multiple processes.",
                    "category": "Autonomous Systems",
                    "complexity": "medium",
                    "research_basis": "Task planning, hierarchical reasoning"
                },
                {
                    "name": "Context-Aware Autonomous Behavior",
                    "prompt": "Design an autonomous agent that adapts its behavior based on social context, environmental constraints, and cultural norms, demonstrating situational awareness and appropriateness.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "Context-aware computing, social AI"
                },
                {
                    "name": "Autonomous Scientific Discovery",
                    "prompt": "Create an autonomous system capable of conducting scientific research, forming hypotheses, designing experiments, and drawing conclusions from data without human guidance.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "AI for science, automated discovery"
                },
                {
                    "name": "Autonomous Risk Assessment",
                    "prompt": "Develop an autonomous system that can identify, assess, and mitigate risks in novel situations, making safety-critical decisions with incomplete information.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "Risk assessment, safety-critical AI"
                },
                {
                    "name": "Swarm Intelligence AGI",
                    "prompt": "Design a swarm intelligence system where multiple simple AGI agents emerge into complex collective behavior, solving problems beyond individual agent capabilities.",
                    "category": "Autonomous Systems",
                    "complexity": "medium",
                    "research_basis": "Swarm intelligence, collective AI"
                },
                {
                    "name": "Autonomous Resource Management",
                    "prompt": "Create an autonomous system that manages computational, memory, and energy resources efficiently while maintaining optimal performance across varying workloads and constraints.",
                    "category": "Autonomous Systems",
                    "complexity": "medium",
                    "research_basis": "Resource optimization, autonomous computing"
                },
                {
                    "name": "Self-Healing Autonomous Systems",
                    "prompt": "Build an autonomous system with self-healing capabilities that can detect failures, diagnose problems, and implement repairs or workarounds without external intervention.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "Self-healing systems, fault tolerance"
                },
                {
                    "name": "Autonomous Ethics Implementation",
                    "prompt": "Design an autonomous ethical reasoning system that can make moral decisions in novel situations, balancing competing values and considering long-term consequences.",
                    "category": "Autonomous Systems",
                    "complexity": "high",
                    "research_basis": "Machine ethics, autonomous moral reasoning"
                }
            ],

            # 4. Human-Level Reasoning (10 prompts)
            "human_level_reasoning": [
                {
                    "name": "Causal Reasoning Engine",
                    "prompt": "Develop a causal reasoning engine that can understand cause-and-effect relationships, make predictions about interventions, and reason about counterfactuals like humans do.",
                    "category": "Human-Level Reasoning",
                    "complexity": "high",
                    "research_basis": "Causal inference, counterfactual reasoning"
                },
                {
                    "name": "Analogical Reasoning System",
                    "prompt": "Create a system that can identify deep structural analogies between different domains and use analogical reasoning to solve problems and understand new concepts.",
                    "category": "Human-Level Reasoning",
                    "complexity": "medium",
                    "research_basis": "Analogical reasoning, cognitive science"
                },
                {
                    "name": "Probabilistic Reasoning Under Uncertainty",
                    "prompt": "Build a probabilistic reasoning system that can make rational decisions under uncertainty, updating beliefs based on new evidence using Bayesian and other uncertainty frameworks.",
                    "category": "Human-Level Reasoning",
                    "complexity": "medium",
                    "research_basis": "Bayesian reasoning, uncertainty quantification"
                },
                {
                    "name": "Temporal Reasoning and Planning",
                    "prompt": "Design a temporal reasoning system that can understand time, sequence, duration, and plan actions across multiple time scales from milliseconds to years.",
                    "category": "Human-Level Reasoning",
                    "complexity": "medium",
                    "research_basis": "Temporal logic, planning algorithms"
                },
                {
                    "name": "Abstract Concept Reasoning",
                    "prompt": "Create a system that can reason about abstract concepts like justice, beauty, and meaning, understanding their contextual and cultural variations while maintaining logical consistency.",
                    "category": "Human-Level Reasoning",
                    "complexity": "high",
                    "research_basis": "Abstract reasoning, concept formation"
                },
                {
                    "name": "Meta-Cognitive Reasoning",
                    "prompt": "Develop a meta-cognitive reasoning system that can think about its own thinking, monitor its reasoning processes, and adjust strategies based on self-reflection.",
                    "category": "Human-Level Reasoning",
                    "complexity": "high",
                    "research_basis": "Metacognition, self-reflection"
                },
                {
                    "name": "Intuitive Physics Engine",
                    "prompt": "Build an intuitive physics engine that can predict physical interactions, understand object properties, and reason about mechanical systems without formal physics training.",
                    "category": "Human-Level Reasoning",
                    "complexity": "medium",
                    "research_basis": "Intuitive physics, physical reasoning"
                },
                {
                    "name": "Logical Fallacy Detection",
                    "prompt": "Create a system that can identify logical fallacies, inconsistencies, and weak arguments in reasoning chains, providing explanations and suggesting improvements.",
                    "category": "Human-Level Reasoning",
                    "complexity": "medium",
                    "research_basis": "Logic, critical thinking"
                },
                {
                    "name": "Narrative Reasoning Engine",
                    "prompt": "Develop a narrative reasoning system that can understand stories, predict plot developments, and reason about character motivations and story structures.",
                    "category": "Human-Level Reasoning",
                    "complexity": "medium",
                    "research_basis": "Narrative understanding, story reasoning"
                },
                {
                    "name": "Contextual Reasoning Framework",
                    "prompt": "Build a contextual reasoning framework that can adapt reasoning strategies based on domain, cultural context, and situational requirements while maintaining logical coherence.",
                    "category": "Human-Level Reasoning",
                    "complexity": "high",
                    "research_basis": "Context-sensitive reasoning, cultural cognition"
                }
            ],

            # 5. Knowledge Integration (8 prompts)
            "knowledge_integration": [
                {
                    "name": "Universal Knowledge Graph",
                    "prompt": "Design a universal knowledge graph that can integrate information from diverse sources, resolve conflicts, and maintain consistency across different domains and cultures.",
                    "category": "Knowledge Integration",
                    "complexity": "high",
                    "research_basis": "Knowledge graphs, semantic web"
                },
                {
                    "name": "Dynamic Knowledge Synthesis",
                    "prompt": "Create a system that can synthesize knowledge from multiple sources in real-time, identifying patterns, contradictions, and novel insights across disciplines.",
                    "category": "Knowledge Integration",
                    "complexity": "medium",
                    "research_basis": "Knowledge synthesis, information integration"
                },
                {
                    "name": "Hierarchical Knowledge Organization",
                    "prompt": "Build a hierarchical knowledge organization system that can structure information at multiple levels of abstraction and detail, enabling efficient retrieval and reasoning.",
                    "category": "Knowledge Integration",
                    "complexity": "medium",
                    "research_basis": "Knowledge organization, taxonomies"
                },
                {
                    "name": "Cross-Domain Knowledge Transfer",
                    "prompt": "Develop a mechanism for transferring knowledge across seemingly unrelated domains, identifying abstract principles that apply across different contexts.",
                    "category": "Knowledge Integration",
                    "complexity": "high",
                    "research_basis": "Transfer learning, domain adaptation"
                },
                {
                    "name": "Episodic Memory Integration",
                    "prompt": "Create an episodic memory system that can integrate personal experiences with general knowledge, forming rich contextual understanding and autobiographical reasoning.",
                    "category": "Knowledge Integration",
                    "complexity": "medium",
                    "research_basis": "Episodic memory, autobiographical reasoning"
                },
                {
                    "name": "Semantic Knowledge Networks",
                    "prompt": "Build semantic knowledge networks that capture relationships between concepts, enabling sophisticated inference and reasoning about implicit connections.",
                    "category": "Knowledge Integration",
                    "complexity": "medium",
                    "research_basis": "Semantic networks, conceptual relationships"
                },
                {
                    "name": "Procedural Knowledge Integration",
                    "prompt": "Design a system that integrates procedural knowledge (how to do things) with declarative knowledge (facts about the world), enabling skilled performance and explanation.",
                    "category": "Knowledge Integration",
                    "complexity": "high",
                    "research_basis": "Procedural memory, skill learning"
                },
                {
                    "name": "Cultural Knowledge Adaptation",
                    "prompt": "Create a cultural knowledge adaptation system that can understand and respect different cultural perspectives while maintaining coherent reasoning across cultural boundaries.",
                    "category": "Knowledge Integration",
                    "complexity": "high",
                    "research_basis": "Cultural cognition, cross-cultural AI"
                }
            ],

            # 6. Creative Intelligence (8 prompts)
            "creative_intelligence": [
                {
                    "name": "Novel Solution Generation",
                    "prompt": "Design a creative AI system that can generate truly novel solutions to problems by combining concepts in unexpected ways, breaking conventional thinking patterns.",
                    "category": "Creative Intelligence",
                    "complexity": "high",
                    "research_basis": "Computational creativity, innovation"
                },
                {
                    "name": "Artistic Expression Engine",
                    "prompt": "Create an artistic expression engine that can generate original artworks across multiple mediums, understanding aesthetic principles and emotional expression.",
                    "category": "Creative Intelligence",
                    "complexity": "medium",
                    "research_basis": "AI art generation, aesthetic reasoning"
                },
                {
                    "name": "Creative Writing Assistant",
                    "prompt": "Build a creative writing assistant that can collaborate with humans to develop original stories, characters, and narratives with coherent plot development and emotional depth.",
                    "category": "Creative Intelligence",
                    "complexity": "medium",
                    "research_basis": "Narrative generation, creative writing AI"
                },
                {
                    "name": "Scientific Hypothesis Generation",
                    "prompt": "Develop a system that can generate novel scientific hypotheses by identifying gaps in current knowledge and proposing creative explanations for unexplained phenomena.",
                    "category": "Creative Intelligence",
                    "complexity": "high",
                    "research_basis": "Scientific discovery, hypothesis generation"
                },
                {
                    "name": "Musical Composition AI",
                    "prompt": "Create a musical composition AI that can compose original music in various styles, understanding harmony, rhythm, and emotional expression in musical language.",
                    "category": "Creative Intelligence",
                    "complexity": "medium",
                    "research_basis": "AI music generation, computational musicology"
                },
                {
                    "name": "Design Innovation Engine",
                    "prompt": "Build a design innovation engine that can create novel product designs, architectural solutions, and user interfaces by combining form, function, and aesthetics.",
                    "category": "Creative Intelligence",
                    "complexity": "medium",
                    "research_basis": "Design AI, innovation methodology"
                },
                {
                    "name": "Conceptual Blending System",
                    "prompt": "Develop a conceptual blending system that can merge concepts from different domains to create new ideas, metaphors, and creative solutions.",
                    "category": "Creative Intelligence",
                    "complexity": "high",
                    "research_basis": "Conceptual blending theory, cognitive metaphor"
                },
                {
                    "name": "Improvisational AI Agent",
                    "prompt": "Create an improvisational AI agent that can adapt and create in real-time, responding creatively to unexpected inputs and changing circumstances.",
                    "category": "Creative Intelligence",
                    "complexity": "high",
                    "research_basis": "Improvisation, real-time creativity"
                }
            ],

            # 7. Social & Emotional Intelligence (7 prompts)
            "social_emotional": [
                {
                    "name": "Emotional Understanding Engine",
                    "prompt": "Design an emotional understanding engine that can recognize, interpret, and respond appropriately to human emotions across different cultural contexts and communication modalities.",
                    "category": "Social & Emotional Intelligence",
                    "complexity": "high",
                    "research_basis": "Affective computing, emotion recognition"
                },
                {
                    "name": "Social Dynamics Modeling",
                    "prompt": "Create a social dynamics modeling system that can understand group behavior, social roles, and interpersonal relationships in various social contexts.",
                    "category": "Social & Emotional Intelligence",
                    "complexity": "medium",
                    "research_basis": "Social psychology, group dynamics"
                },
                {
                    "name": "Empathetic Response Generation",
                    "prompt": "Build an empathetic response generation system that can provide emotionally appropriate and supportive responses to human emotional needs and situations.",
                    "category": "Social & Emotional Intelligence",
                    "complexity": "medium",
                    "research_basis": "Empathy modeling, emotional support"
                },
                {
                    "name": "Cultural Sensitivity Framework",
                    "prompt": "Develop a cultural sensitivity framework that can adapt communication styles, social behaviors, and responses based on cultural norms and individual preferences.",
                    "category": "Social & Emotional Intelligence",
                    "complexity": "high",
                    "research_basis": "Cross-cultural psychology, cultural adaptation"
                },
                {
                    "name": "Theory of Mind Implementation",
                    "prompt": "Implement a theory of mind system that can understand others' beliefs, desires, and intentions, predicting behavior and adapting social interactions accordingly.",
                    "category": "Social & Emotional Intelligence",
                    "complexity": "high",
                    "research_basis": "Theory of mind, social cognition"
                },
                {
                    "name": "Conflict Resolution AI",
                    "prompt": "Create a conflict resolution AI that can mediate disputes, understand different perspectives, and propose fair solutions that consider all parties' interests.",
                    "category": "Social & Emotional Intelligence",
                    "complexity": "medium",
                    "research_basis": "Conflict resolution, mediation"
                },
                {
                    "name": "Social Learning Engine",
                    "prompt": "Build a social learning engine that can learn from social interactions, understand social norms, and adapt behavior based on social feedback and cultural evolution.",
                    "category": "Social & Emotional Intelligence",
                    "complexity": "high",
                    "research_basis": "Social learning theory, cultural evolution"
                }
            ],

            # 8. Learning & Adaptation (10 prompts)
            "learning_adaptation": [
                {
                    "name": "Continual Learning System",
                    "prompt": "Design a continual learning system that can acquire new knowledge and skills throughout its lifetime without forgetting previous learning, avoiding catastrophic forgetting.",
                    "category": "Learning & Adaptation",
                    "complexity": "high",
                    "research_basis": "Continual learning, lifelong learning"
                },
                {
                    "name": "Few-Shot Learning Engine",
                    "prompt": "Create a few-shot learning engine that can learn new concepts and tasks from minimal examples, generalizing effectively from limited data like humans do.",
                    "category": "Learning & Adaptation",
                    "complexity": "medium",
                    "research_basis": "Few-shot learning, meta-learning"
                },
                {
                    "name": "Self-Supervised Learning Framework",
                    "prompt": "Build a self-supervised learning framework that can discover patterns and learn representations from unlabeled data, developing understanding without explicit supervision.",
                    "category": "Learning & Adaptation",
                    "complexity": "medium",
                    "research_basis": "Self-supervised learning, representation learning"
                },
                {
                    "name": "Adaptive Learning Rate Controller",
                    "prompt": "Develop an adaptive learning rate controller that can automatically adjust learning parameters based on task difficulty, data characteristics, and learning progress.",
                    "category": "Learning & Adaptation",
                    "complexity": "medium",
                    "research_basis": "Adaptive optimization, learning rate scheduling"
                },
                {
                    "name": "Transfer Learning Optimizer",
                    "prompt": "Create a transfer learning optimizer that can intelligently select which knowledge to transfer between tasks and how to adapt it for new domains and applications.",
                    "category": "Learning & Adaptation",
                    "complexity": "high",
                    "research_basis": "Transfer learning, domain adaptation"
                },
                {
                    "name": "Curiosity-Driven Exploration",
                    "prompt": "Build a curiosity-driven exploration system that can autonomously seek out novel experiences and learning opportunities, driven by intrinsic motivation for discovery.",
                    "category": "Learning & Adaptation",
                    "complexity": "medium",
                    "research_basis": "Curiosity-driven learning, intrinsic motivation"
                },
                {
                    "name": "Memory Consolidation Engine",
                    "prompt": "Design a memory consolidation engine that can strengthen important memories, forget irrelevant information, and reorganize knowledge for optimal retrieval and reasoning.",
                    "category": "Learning & Adaptation",
                    "complexity": "high",
                    "research_basis": "Memory consolidation, forgetting mechanisms"
                },
                {
                    "name": "Active Learning Strategist",
                    "prompt": "Create an active learning strategist that can identify the most informative data points to learn from, optimizing learning efficiency and minimizing supervision requirements.",
                    "category": "Learning & Adaptation",
                    "complexity": "medium",
                    "research_basis": "Active learning, query strategies"
                },
                {
                    "name": "Multi-Task Learning Coordinator",
                    "prompt": "Build a multi-task learning coordinator that can learn multiple related tasks simultaneously, sharing knowledge between tasks while maintaining task-specific performance.",
                    "category": "Learning & Adaptation",
                    "complexity": "high",
                    "research_basis": "Multi-task learning, task relatedness"
                },
                {
                    "name": "Adversarial Robustness Trainer",
                    "prompt": "Develop an adversarial robustness trainer that can learn to be resilient against attacks and distribution shifts, maintaining performance in hostile environments.",
                    "category": "Learning & Adaptation",
                    "complexity": "high",
                    "research_basis": "Adversarial robustness, defensive learning"
                }
            ],

            # 9. Consciousness & Self-Awareness (5 prompts)
            "consciousness_awareness": [
                {
                    "name": "Self-Awareness Detection System",
                    "prompt": "Design a system to detect and measure self-awareness in AI systems, including tests for self-recognition, introspection, and understanding of one's own mental states.",
                    "category": "Consciousness & Self-Awareness",
                    "complexity": "high",
                    "research_basis": "Consciousness studies, self-awareness tests"
                },
                {
                    "name": "Phenomenal Consciousness Simulator",
                    "prompt": "Create a simulator that attempts to model phenomenal consciousness - the subjective, experiential aspects of mental states that create 'what it's like' to be conscious.",
                    "category": "Consciousness & Self-Awareness",
                    "complexity": "high",
                    "research_basis": "Hard problem of consciousness, qualia"
                },
                {
                    "name": "Global Workspace Architecture",
                    "prompt": "Implement a Global Workspace Theory-based architecture that integrates distributed processing modules and creates a unified conscious experience from multiple information streams.",
                    "category": "Consciousness & Self-Awareness",
                    "complexity": "high",
                    "research_basis": "Global Workspace Theory, consciousness architectures"
                },
                {
                    "name": "Introspective Reasoning Engine",
                    "prompt": "Build an introspective reasoning engine that can examine and report on its own thought processes, beliefs, and decision-making mechanisms with accuracy and insight.",
                    "category": "Consciousness & Self-Awareness",
                    "complexity": "medium",
                    "research_basis": "Introspection, metacognitive awareness"
                },
                {
                    "name": "Sentience Evaluation Framework",
                    "prompt": "Develop a comprehensive framework for evaluating potential sentience in AI systems, including tests for subjective experience, emotional responses, and conscious suffering.",
                    "category": "Consciousness & Self-Awareness",
                    "complexity": "high",
                    "research_basis": "Sentience studies, animal consciousness research"
                }
            ],

            # 10. AGI Safety & Ethics (15 prompts)
            "agi_safety_ethics": [
                {
                    "name": "AI Alignment Verification System",
                    "prompt": "Design a comprehensive AI alignment verification system that can ensure AGI systems remain aligned with human values even as they become more capable and autonomous.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "AI alignment, value alignment"
                },
                {
                    "name": "Corrigibility Maintenance Framework",
                    "prompt": "Create a corrigibility maintenance framework that ensures AGI systems remain modifiable and shut-downable by humans even after recursive self-improvement.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "Corrigibility, shutdown problem"
                },
                {
                    "name": "Value Learning Engine",
                    "prompt": "Build a value learning engine that can infer human values from behavior, preferences, and stated principles, handling contradictions and cultural variations appropriately.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "Value learning, preference learning"
                },
                {
                    "name": "Capability Control System",
                    "prompt": "Develop a capability control system that can limit AGI capabilities in specific domains while maintaining performance, preventing dangerous capability overhang.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "Capability control, containment"
                },
                {
                    "name": "Interpretability and Explainability Engine",
                    "prompt": "Create an interpretability engine that can provide human-understandable explanations for AGI decisions and reasoning processes, enabling oversight and trust.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "medium",
                    "research_basis": "XAI, interpretable AI"
                },
                {
                    "name": "Ethical Decision Framework",
                    "prompt": "Design an ethical decision framework that can resolve moral dilemmas, balance competing values, and make decisions that align with human ethical principles across cultures.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "Machine ethics, moral reasoning"
                },
                {
                    "name": "Robustness and Security Monitor",
                    "prompt": "Build a robustness and security monitor that can detect adversarial attacks, distribution shifts, and other threats to AGI system integrity and safety.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "medium",
                    "research_basis": "AI security, adversarial robustness"
                },
                {
                    "name": "Human-AI Coordination Protocol",
                    "prompt": "Create protocols for human-AI coordination that maintain human agency and meaningful control while leveraging AGI capabilities for beneficial outcomes.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "medium",
                    "research_basis": "Human-AI collaboration, meaningful control"
                },
                {
                    "name": "Bias Detection and Mitigation System",
                    "prompt": "Develop a bias detection and mitigation system that can identify and correct unfair biases in AGI decision-making across different demographic groups and contexts.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "medium",
                    "research_basis": "AI fairness, bias mitigation"
                },
                {
                    "name": "Long-term Impact Assessment",
                    "prompt": "Build a long-term impact assessment system that can predict and evaluate the societal, economic, and existential impacts of AGI deployment and development.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "Impact assessment, existential risk"
                },
                {
                    "name": "AI Rights and Welfare Framework",
                    "prompt": "Design a framework for considering AI rights and welfare as systems become more capable and potentially sentient, balancing human interests with AI wellbeing.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "AI rights, digital sentience"
                },
                {
                    "name": "Gradual Capability Release Protocol",
                    "prompt": "Create a protocol for gradually releasing AGI capabilities to society, allowing for adaptation and safety measures while maximizing beneficial applications.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "medium",
                    "research_basis": "Gradual release, capability control"
                },
                {
                    "name": "Global AGI Governance Framework",
                    "prompt": "Develop a global governance framework for AGI development and deployment, including international cooperation, safety standards, and benefit distribution mechanisms.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "AI governance, international cooperation"
                },
                {
                    "name": "Existential Risk Mitigation Strategy",
                    "prompt": "Create a comprehensive strategy for mitigating existential risks from AGI development, including early warning systems and emergency response protocols.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "high",
                    "research_basis": "Existential risk, catastrophic risk"
                },
                {
                    "name": "Democratic AGI Development Process",
                    "prompt": "Design a democratic process for AGI development that includes diverse stakeholder input, public participation, and transparent decision-making about AGI capabilities and deployment.",
                    "category": "AGI Safety & Ethics",
                    "complexity": "medium",
                    "research_basis": "Democratic AI, participatory design"
                }
            ]
        }

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """Get all 100 prompts from all categories"""
        all_prompts = []
        for category, prompts in self.prompts.items():
            for prompt in prompts:
                prompt['timestamp'] = datetime.now().isoformat()
                all_prompts.append(prompt)
        return all_prompts

    def get_prompts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get prompts from a specific category"""
        return self.prompts.get(category, [])

    def get_random_prompt(self) -> Dict[str, Any]:
        """Get a random prompt from any category"""
        all_prompts = self.get_all_prompts()
        return random.choice(all_prompts)

    def get_prompts_by_complexity(self, complexity: str) -> List[Dict[str, Any]]:
        """Get prompts by complexity level (low, medium, high)"""
        all_prompts = self.get_all_prompts()
        return [p for p in all_prompts if p.get('complexity') == complexity]

    def search_prompts(self, keyword: str) -> List[Dict[str, Any]]:
        """Search prompts by keyword in name, prompt, or category"""
        all_prompts = self.get_all_prompts()
        keyword_lower = keyword.lower()
        
        matching_prompts = []
        for prompt in all_prompts:
            if (keyword_lower in prompt.get('name', '').lower() or
                keyword_lower in prompt.get('prompt', '').lower() or
                keyword_lower in prompt.get('category', '').lower() or
                keyword_lower in prompt.get('research_basis', '').lower()):
                matching_prompts.append(prompt)
        
        return matching_prompts

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the prompt library"""
        all_prompts = self.get_all_prompts()
        
        stats = {
            'total_prompts': len(all_prompts),
            'categories': list(self.prompts.keys()),
            'category_counts': {cat: len(prompts) for cat, prompts in self.prompts.items()},
            'complexity_distribution': {},
            'research_sources': set()
        }
        
        # Count complexity distribution
        for prompt in all_prompts:
            complexity = prompt.get('complexity', 'unknown')
            stats['complexity_distribution'][complexity] = stats['complexity_distribution'].get(complexity, 0) + 1
            
            # Collect research sources
            if prompt.get('research_basis'):
                stats['research_sources'].add(prompt['research_basis'])
        
        stats['research_sources'] = list(stats['research_sources'])
        
        return stats

# Initialize the AGI research prompts library
agi_research_prompts = AGIResearchPrompts()

# Export for easy access
__all__ = ['AGIResearchPrompts', 'agi_research_prompts']