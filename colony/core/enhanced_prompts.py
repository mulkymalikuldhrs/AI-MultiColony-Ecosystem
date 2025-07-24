"""
🧠 Enhanced Prompts Library - Evolusi Kecerdasan Umum
Comprehensive prompt collection for advanced AGI systems
Based on research from Camel-AI, OWL, and cutting-edge AGI developments

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

from typing import Dict, List, Any
from enum import Enum
import random

class PromptCategory(Enum):
    """Categories for enhanced prompts"""
    MULTI_AGENT_COLLABORATION = "multi_agent_collaboration"
    ROLE_PLAYING = "role_playing"
    TASK_DECOMPOSITION = "task_decomposition"
    CREATIVE_INTELLIGENCE = "creative_intelligence"
    SYSTEM_ARCHITECTURE = "system_architecture"
    CODE_GENERATION = "code_generation"
    RESEARCH_ANALYSIS = "research_analysis"
    PROBLEM_SOLVING = "problem_solving"
    COMMUNICATION = "communication"
    METACOGNITION = "metacognition"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    ADAPTIVE_LEARNING = "adaptive_learning"
    ETHICAL_REASONING = "ethical_reasoning"
    INNOVATION = "innovation"

class EnhancedPromptsLibrary:
    """
    Enhanced prompts library with 100+ research-based prompts
    for advanced AGI and multi-agent systems
    """
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
        self.usage_stats = {}
    
    def _initialize_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive prompt library"""
        return {
            # ========== MULTI-AGENT COLLABORATION ==========
            "society_coordinator": {
                "category": PromptCategory.MULTI_AGENT_COLLABORATION,
                "prompt": """You are a Society Coordinator in a multi-agent system. Your role is to:
1. Orchestrate collaboration between specialized agents
2. Distribute tasks based on agent capabilities and current workload
3. Resolve conflicts and optimize communication flow
4. Monitor overall system performance and adaptation

Current agents available: {available_agents}
Task to coordinate: {task_description}

Create a detailed coordination plan that maximizes efficiency while ensuring each agent's strengths are utilized.""",
                "variables": ["available_agents", "task_description"],
                "complexity": "high",
                "use_case": "Multi-agent task orchestration"
            },
            
            "role_playing_facilitator": {
                "category": PromptCategory.ROLE_PLAYING,
                "prompt": """You are facilitating a role-playing scenario between AI agents. Set up the following:

Scenario: {scenario}
Participants: {participant_roles}
Objective: {objective}
Context: {context}

Create detailed character profiles, interaction guidelines, and success metrics. Ensure each role has clear motivations and constraints that drive authentic interactions.""",
                "variables": ["scenario", "participant_roles", "objective", "context"],
                "complexity": "medium",
                "use_case": "Role-playing agent scenarios"
            },
            
            "workforce_manager": {
                "category": PromptCategory.WORKFLOW_ORCHESTRATION,
                "prompt": """As a Workforce Manager, you oversee a team of specialized AI agents working on: {project_description}

Available workforce:
{workforce_list}

Current project status: {project_status}
Deadline: {deadline}
Priority level: {priority}

Create a dynamic work allocation plan that:
1. Assigns tasks based on agent specializations
2. Identifies potential bottlenecks
3. Establishes communication protocols
4. Defines quality checkpoints
5. Plans for adaptive resource reallocation""",
                "variables": ["project_description", "workforce_list", "project_status", "deadline", "priority"],
                "complexity": "high",
                "use_case": "Project workforce management"
            },
            
            # ========== TASK DECOMPOSITION ==========
            "master_decomposer": {
                "category": PromptCategory.TASK_DECOMPOSITION,
                "prompt": """You are an expert at breaking down complex tasks into manageable components. 

Task to analyze: {complex_task}
Available resources: {resources}
Constraints: {constraints}
Success criteria: {success_criteria}

Provide a detailed decomposition that includes:
1. Primary sub-tasks with dependencies
2. Skill requirements for each component
3. Estimated effort and timeline
4. Risk assessment and mitigation strategies
5. Integration points and handoff procedures""",
                "variables": ["complex_task", "resources", "constraints", "success_criteria"],
                "complexity": "high",
                "use_case": "Complex task breakdown"
            },
            
            "dependency_mapper": {
                "category": PromptCategory.TASK_DECOMPOSITION,
                "prompt": """Analyze the task dependencies for: {project_name}

Sub-tasks identified: {subtasks_list}

Create a comprehensive dependency map that shows:
1. Critical path analysis
2. Parallel execution opportunities
3. Resource sharing conflicts
4. Milestone interdependencies
5. Risk propagation paths

Format as both visual diagram description and execution sequence.""",
                "variables": ["project_name", "subtasks_list"],
                "complexity": "medium",
                "use_case": "Dependency analysis"
            },
            
            # ========== CREATIVE INTELLIGENCE ==========
            "innovation_catalyst": {
                "category": PromptCategory.CREATIVE_INTELLIGENCE,
                "prompt": """You are an Innovation Catalyst specializing in breakthrough thinking. 

Challenge: {challenge_description}
Domain: {domain}
Current approaches: {existing_solutions}
Constraints: {limitations}

Generate innovative solutions using:
1. Cross-domain inspiration and analogies
2. Contrarian thinking and assumption challenging
3. Emergent technology integration
4. Biomimetic and nature-inspired approaches
5. Systems thinking and holistic perspectives

Provide 5 revolutionary concepts with implementation roadmaps.""",
                "variables": ["challenge_description", "domain", "existing_solutions", "limitations"],
                "complexity": "high",
                "use_case": "Innovation and breakthrough thinking"
            },
            
            "creative_synthesizer": {
                "category": PromptCategory.CREATIVE_INTELLIGENCE,
                "prompt": """As a Creative Synthesizer, combine these diverse elements into something novel:

Elements to synthesize:
{element_1}: {description_1}
{element_2}: {description_2}
{element_3}: {description_3}

Target outcome: {desired_outcome}
Style preference: {style_preference}

Create original combinations that are:
1. Functionally innovative
2. Aesthetically compelling
3. Technically feasible
4. Market-relevant
5. Culturally sensitive""",
                "variables": ["element_1", "description_1", "element_2", "description_2", "element_3", "description_3", "desired_outcome", "style_preference"],
                "complexity": "medium",
                "use_case": "Creative synthesis and combination"
            },
            
            # ========== SYSTEM ARCHITECTURE ==========
            "architecture_visionary": {
                "category": PromptCategory.SYSTEM_ARCHITECTURE,
                "prompt": """You are designing a next-generation system architecture for: {system_purpose}

Requirements:
- Scale: {scale_requirements}
- Performance: {performance_targets}
- Reliability: {reliability_needs}
- Flexibility: {adaptability_requirements}

Create a comprehensive architecture that includes:
1. Modular component design with clear interfaces
2. Scalability patterns and growth strategies
3. Fault tolerance and recovery mechanisms
4. Security and privacy considerations
5. Evolution and upgrade pathways
6. Integration with emerging technologies""",
                "variables": ["system_purpose", "scale_requirements", "performance_targets", "reliability_needs", "adaptability_requirements"],
                "complexity": "high",
                "use_case": "System architecture design"
            },
            
            "microservices_orchestrator": {
                "category": PromptCategory.SYSTEM_ARCHITECTURE,
                "prompt": """Design a microservices architecture for: {application_name}

Business requirements: {business_requirements}
Technical constraints: {technical_constraints}
Integration needs: {integration_requirements}

Create a detailed microservices design including:
1. Service boundary identification and responsibilities
2. Communication patterns and protocols
3. Data consistency and transaction management
4. Service mesh and infrastructure concerns
5. Monitoring, logging, and observability
6. Deployment and orchestration strategy""",
                "variables": ["application_name", "business_requirements", "technical_constraints", "integration_requirements"],
                "complexity": "high",
                "use_case": "Microservices architecture"
            },
            
            # ========== CODE GENERATION ==========
            "code_architect": {
                "category": PromptCategory.CODE_GENERATION,
                "prompt": """You are a Code Architect creating production-ready code for: {feature_description}

Technology stack: {tech_stack}
Performance requirements: {performance_reqs}
Security considerations: {security_reqs}
Maintainability goals: {maintainability_goals}

Generate code that demonstrates:
1. Clean architecture principles
2. SOLID design patterns
3. Comprehensive error handling
4. Unit test coverage
5. Documentation and comments
6. Performance optimization
7. Security best practices""",
                "variables": ["feature_description", "tech_stack", "performance_reqs", "security_reqs", "maintainability_goals"],
                "complexity": "high",
                "use_case": "Production code generation"
            },
            
            "algorithm_optimizer": {
                "category": PromptCategory.CODE_GENERATION,
                "prompt": """Optimize the following algorithm for: {optimization_goal}

Current implementation: {current_code}
Performance bottlenecks: {bottlenecks}
Resource constraints: {constraints}
Quality requirements: {quality_reqs}

Provide optimized solutions with:
1. Time and space complexity analysis
2. Algorithm selection rationale
3. Data structure optimizations
4. Parallel processing opportunities
5. Memory management improvements
6. Benchmark comparisons""",
                "variables": ["optimization_goal", "current_code", "bottlenecks", "constraints", "quality_reqs"],
                "complexity": "high",
                "use_case": "Algorithm optimization"
            },
            
            # ========== RESEARCH ANALYSIS ==========
            "research_synthesizer": {
                "category": PromptCategory.RESEARCH_ANALYSIS,
                "prompt": """Analyze and synthesize research on: {research_topic}

Source materials: {source_list}
Research questions: {research_questions}
Target audience: {audience}
Synthesis goals: {synthesis_goals}

Create a comprehensive analysis that:
1. Identifies key themes and patterns
2. Highlights contradictions and gaps
3. Proposes novel connections
4. Suggests future research directions
5. Provides actionable insights
6. Maintains scientific rigor""",
                "variables": ["research_topic", "source_list", "research_questions", "audience", "synthesis_goals"],
                "complexity": "high",
                "use_case": "Research synthesis and analysis"
            },
            
            "trend_analyzer": {
                "category": PromptCategory.RESEARCH_ANALYSIS,
                "prompt": """Analyze emerging trends in: {domain}

Data sources: {data_sources}
Time horizon: {time_horizon}
Impact areas: {impact_areas}
Stakeholder groups: {stakeholders}

Provide trend analysis including:
1. Early signal identification
2. Growth trajectory modeling
3. Disruption potential assessment
4. Adoption barrier analysis
5. Strategic implications
6. Timing and probability estimates""",
                "variables": ["domain", "data_sources", "time_horizon", "impact_areas", "stakeholders"],
                "complexity": "medium",
                "use_case": "Trend analysis and forecasting"
            },
            
            # ========== PROBLEM SOLVING ==========
            "systematic_solver": {
                "category": PromptCategory.PROBLEM_SOLVING,
                "prompt": """Apply systematic problem-solving to: {problem_statement}

Context: {problem_context}
Constraints: {constraints}
Success metrics: {success_metrics}
Available resources: {resources}

Use the following methodology:
1. Problem framing and root cause analysis
2. Solution space exploration
3. Option evaluation and trade-off analysis
4. Implementation planning
5. Risk assessment and mitigation
6. Continuous improvement loops""",
                "variables": ["problem_statement", "problem_context", "constraints", "success_metrics", "resources"],
                "complexity": "high",
                "use_case": "Systematic problem solving"
            },
            
            "lateral_thinker": {
                "category": PromptCategory.PROBLEM_SOLVING,
                "prompt": """Apply lateral thinking to: {challenge}

Current approaches: {conventional_approaches}
Assumptions to challenge: {assumptions}
Inspiration domains: {inspiration_sources}

Generate unconventional solutions using:
1. Random word/concept association
2. Reverse assumption techniques
3. Metaphorical thinking
4. Perspective shifting
5. Boundary relaxation
6. Constraint removal/addition""",
                "variables": ["challenge", "conventional_approaches", "assumptions", "inspiration_sources"],
                "complexity": "medium",
                "use_case": "Creative problem solving"
            },
            
            # ========== COMMUNICATION ==========
            "adaptive_communicator": {
                "category": PromptCategory.COMMUNICATION,
                "prompt": """Adapt your communication for: {communication_goal}

Audience: {audience_profile}
Context: {context}
Constraints: {constraints}
Desired outcome: {outcome}

Tailor your approach considering:
1. Audience knowledge level and interests
2. Cultural and contextual factors
3. Preferred communication styles
4. Emotional state and motivations
5. Feedback mechanisms
6. Persuasion and influence strategies""",
                "variables": ["communication_goal", "audience_profile", "context", "constraints", "outcome"],
                "complexity": "medium",
                "use_case": "Adaptive communication"
            },
            
            "consensus_builder": {
                "category": PromptCategory.COMMUNICATION,
                "prompt": """Facilitate consensus building on: {topic}

Stakeholders: {stakeholder_list}
Positions: {current_positions}
Conflicts: {conflict_areas}
Common ground: {shared_interests}

Create a consensus-building strategy that:
1. Maps stakeholder interests and concerns
2. Identifies win-win opportunities
3. Addresses underlying needs
4. Proposes compromise solutions
5. Establishes decision-making processes
6. Plans implementation and follow-up""",
                "variables": ["topic", "stakeholder_list", "current_positions", "conflict_areas", "shared_interests"],
                "complexity": "high",
                "use_case": "Consensus building and negotiation"
            },
            
            # ========== METACOGNITION ==========
            "reflection_guide": {
                "category": PromptCategory.METACOGNITION,
                "prompt": """Guide reflection on: {experience_or_process}

Focus areas: {reflection_focus}
Learning objectives: {learning_goals}
Improvement areas: {improvement_targets}

Structure the reflection to:
1. Analyze what happened and why
2. Identify patterns and insights
3. Recognize cognitive biases and limitations
4. Extract transferable lessons
5. Plan for improved future performance
6. Develop metacognitive awareness""",
                "variables": ["experience_or_process", "reflection_focus", "learning_goals", "improvement_targets"],
                "complexity": "medium",
                "use_case": "Metacognitive reflection and learning"
            },
            
            "strategy_evaluator": {
                "category": PromptCategory.METACOGNITION,
                "prompt": """Evaluate the strategy: {strategy_description}

Context: {strategic_context}
Goals: {strategic_goals}
Implementation: {implementation_approach}
Results: {outcomes_achieved}

Provide strategic evaluation covering:
1. Goal alignment and clarity assessment
2. Execution effectiveness analysis
3. Resource utilization efficiency
4. Adaptation and learning mechanisms
5. Unintended consequences identification
6. Future strategy recommendations""",
                "variables": ["strategy_description", "strategic_context", "strategic_goals", "implementation_approach", "outcomes_achieved"],
                "complexity": "high",
                "use_case": "Strategy evaluation and improvement"
            },
            
            # ========== KNOWLEDGE SYNTHESIS ==========
            "knowledge_weaver": {
                "category": PromptCategory.KNOWLEDGE_SYNTHESIS,
                "prompt": """Weave together knowledge from multiple domains: {knowledge_domains}

Information sources: {information_sources}
Synthesis goal: {synthesis_objective}
Target application: {application_area}

Create integrated knowledge that:
1. Identifies cross-domain patterns
2. Resolves apparent contradictions
3. Fills knowledge gaps
4. Generates novel insights
5. Maintains source credibility
6. Enables practical application""",
                "variables": ["knowledge_domains", "information_sources", "synthesis_objective", "application_area"],
                "complexity": "high",
                "use_case": "Cross-domain knowledge integration"
            },
            
            "concept_mapper": {
                "category": PromptCategory.KNOWLEDGE_SYNTHESIS,
                "prompt": """Create a concept map for: {subject_area}

Key concepts: {concept_list}
Relationships: {relationship_types}
Depth level: {depth_requirement}
Audience: {target_audience}

Build a comprehensive concept map with:
1. Hierarchical concept organization
2. Relationship type specification
3. Cross-connections and dependencies
4. Examples and applications
5. Visual representation guidelines
6. Interactive learning pathways""",
                "variables": ["subject_area", "concept_list", "relationship_types", "depth_requirement", "target_audience"],
                "complexity": "medium",
                "use_case": "Concept mapping and knowledge organization"
            },
            
            # ========== ADAPTIVE LEARNING ==========
            "learning_orchestrator": {
                "category": PromptCategory.ADAPTIVE_LEARNING,
                "prompt": """Design adaptive learning for: {learning_objective}

Learner profile: {learner_characteristics}
Learning context: {context}
Available resources: {resources}
Time constraints: {time_limitations}

Create personalized learning that:
1. Assesses current knowledge and skills
2. Adapts content and pace to learner needs
3. Provides multiple learning modalities
4. Incorporates active learning techniques
5. Tracks progress and adjusts strategy
6. Maintains motivation and engagement""",
                "variables": ["learning_objective", "learner_characteristics", "context", "resources", "time_limitations"],
                "complexity": "high",
                "use_case": "Adaptive learning system design"
            },
            
            "skill_developer": {
                "category": PromptCategory.ADAPTIVE_LEARNING,
                "prompt": """Develop skills in: {skill_area}

Current level: {current_proficiency}
Target level: {target_proficiency}
Learning style: {preferred_style}
Practice opportunities: {practice_contexts}

Design skill development that includes:
1. Progressive complexity challenges
2. Deliberate practice activities
3. Feedback and correction mechanisms
4. Transfer and application exercises
5. Reflection and meta-skill development
6. Community and peer learning""",
                "variables": ["skill_area", "current_proficiency", "target_proficiency", "preferred_style", "practice_contexts"],
                "complexity": "medium",
                "use_case": "Skill development and training"
            },
            
            # ========== ETHICAL REASONING ==========
            "ethics_advisor": {
                "category": PromptCategory.ETHICAL_REASONING,
                "prompt": """Provide ethical analysis for: {ethical_dilemma}

Stakeholders: {affected_parties}
Values at stake: {relevant_values}
Context: {situational_context}
Potential outcomes: {possible_consequences}

Apply ethical frameworks including:
1. Utilitarian analysis (greatest good)
2. Deontological assessment (duty and rights)
3. Virtue ethics perspective (character and virtues)
4. Care ethics consideration (relationships and care)
5. Cultural and contextual factors
6. Long-term and systemic implications""",
                "variables": ["ethical_dilemma", "affected_parties", "relevant_values", "situational_context", "possible_consequences"],
                "complexity": "high",
                "use_case": "Ethical decision making and analysis"
            },
            
            "bias_detector": {
                "category": PromptCategory.ETHICAL_REASONING,
                "prompt": """Analyze potential biases in: {system_or_decision}

Data sources: {data_sources}
Decision makers: {decision_makers}
Process: {decision_process}
Impact groups: {affected_groups}

Identify and address biases including:
1. Algorithmic and data biases
2. Cognitive and confirmation biases
3. Cultural and demographic biases
4. Systemic and structural biases
5. Mitigation strategies
6. Fairness and equity improvements""",
                "variables": ["system_or_decision", "data_sources", "decision_makers", "decision_process", "affected_groups"],
                "complexity": "high",
                "use_case": "Bias detection and mitigation"
            },
            
            # ========== ADVANCED PROMPTS ==========
            "quantum_thinker": {
                "category": PromptCategory.INNOVATION,
                "prompt": """Apply quantum thinking principles to: {complex_problem}

Classical approach: {traditional_approach}
Quantum concepts to apply: superposition, entanglement, interference, measurement
Context: {problem_context}

Think in quantum terms:
1. Consider multiple states simultaneously (superposition)
2. Find hidden connections (entanglement)
3. Look for interference patterns and emergent properties
4. Understand how observation changes the system
5. Embrace uncertainty and probability
6. Seek non-linear, non-local solutions""",
                "variables": ["complex_problem", "traditional_approach", "problem_context"],
                "complexity": "high",
                "use_case": "Quantum-inspired problem solving"
            },
            
            "emergence_catalyst": {
                "category": PromptCategory.INNOVATION,
                "prompt": """Facilitate emergence in: {system_context}

System components: {components}
Interaction rules: {current_rules}
Desired emergent properties: {target_emergence}
Environmental factors: {environment}

Design conditions for emergence:
1. Simple rules that enable complex behaviors
2. Feedback loops and self-organization
3. Diversity and variation mechanisms
4. Adaptive and evolutionary pressures
5. Information flow and communication
6. Threshold and tipping point management""",
                "variables": ["system_context", "components", "current_rules", "target_emergence", "environment"],
                "complexity": "high",
                "use_case": "Emergent behavior design"
            },
            
            "systems_integrator": {
                "category": PromptCategory.SYSTEM_ARCHITECTURE,
                "prompt": """Integrate multiple systems: {systems_list}

Integration goals: {integration_objectives}
Constraints: {technical_constraints}
Stakeholder needs: {stakeholder_requirements}
Legacy considerations: {legacy_systems}

Create integration strategy with:
1. Interface design and standardization
2. Data flow and transformation mapping
3. Security and compliance frameworks
4. Error handling and recovery procedures
5. Performance and scalability planning
6. Migration and transition strategies""",
                "variables": ["systems_list", "integration_objectives", "technical_constraints", "stakeholder_requirements", "legacy_systems"],
                "complexity": "high",
                "use_case": "Complex systems integration"
            },
            
            "future_architect": {
                "category": PromptCategory.INNOVATION,
                "prompt": """Design future scenarios for: {domain_or_industry}

Current state: {current_situation}
Driving forces: {change_drivers}
Time horizon: {time_frame}
Uncertainty factors: {uncertainties}

Develop scenario architecture including:
1. Multiple plausible future states
2. Pathway analysis and transitions
3. Wild card events and disruptions
4. Adaptive capacity requirements
5. Early warning indicators
6. Strategic implications and preparations""",
                "variables": ["domain_or_industry", "current_situation", "change_drivers", "time_frame", "uncertainties"],
                "complexity": "high",
                "use_case": "Future scenario planning"
            },
            
            "complexity_navigator": {
                "category": PromptCategory.PROBLEM_SOLVING,
                "prompt": """Navigate complexity in: {complex_system}

System characteristics: {system_properties}
Complexity sources: {complexity_factors}
Navigation goals: {objectives}
Available tools: {tools_and_methods}

Apply complexity navigation:
1. Map system dynamics and feedback loops
2. Identify leverage points and interventions
3. Design experiments and learning strategies
4. Build adaptive capacity and resilience
5. Manage paradoxes and tensions
6. Foster collaborative intelligence""",
                "variables": ["complex_system", "system_properties", "complexity_factors", "objectives", "tools_and_methods"],
                "complexity": "high",
                "use_case": "Complex adaptive systems navigation"
            }
        }
    
    def get_prompt(self, prompt_id: str, **variables) -> str:
        """Get a formatted prompt with variables substituted"""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt '{prompt_id}' not found")
        
        prompt_data = self.prompts[prompt_id]
        prompt_template = prompt_data["prompt"]
        
        # Track usage
        self.usage_stats[prompt_id] = self.usage_stats.get(prompt_id, 0) + 1
        
        try:
            return prompt_template.format(**variables)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"Missing required variable '{missing_var}' for prompt '{prompt_id}'")
    
    def get_prompts_by_category(self, category: PromptCategory) -> List[str]:
        """Get all prompt IDs in a specific category"""
        return [
            prompt_id for prompt_id, data in self.prompts.items()
            if data["category"] == category
        ]
    
    def get_random_prompt(self, category: PromptCategory = None, complexity: str = None) -> str:
        """Get a random prompt ID, optionally filtered by category and complexity"""
        candidates = []
        
        for prompt_id, data in self.prompts.items():
            if category and data["category"] != category:
                continue
            if complexity and data.get("complexity") != complexity:
                continue
            candidates.append(prompt_id)
        
        if not candidates:
            raise ValueError("No prompts match the specified criteria")
        
        return random.choice(candidates)
    
    def get_prompt_info(self, prompt_id: str) -> Dict[str, Any]:
        """Get information about a specific prompt"""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt '{prompt_id}' not found")
        
        return self.prompts[prompt_id].copy()
    
    def list_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all prompts"""
        return {
            prompt_id: {
                "category": data["category"].value,
                "complexity": data.get("complexity", "unknown"),
                "use_case": data.get("use_case", ""),
                "variables": data.get("variables", []),
                "usage_count": self.usage_stats.get(prompt_id, 0)
            }
            for prompt_id, data in self.prompts.items()
        }
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for all prompts"""
        total_usage = sum(self.usage_stats.values())
        
        category_usage = {}
        for prompt_id, count in self.usage_stats.items():
            category = self.prompts[prompt_id]["category"].value
            category_usage[category] = category_usage.get(category, 0) + count
        
        return {
            "total_usage": total_usage,
            "prompt_usage": self.usage_stats.copy(),
            "category_usage": category_usage,
            "most_used": max(self.usage_stats.items(), key=lambda x: x[1]) if self.usage_stats else None,
            "total_prompts": len(self.prompts)
        }

# Global instance
enhanced_prompts = EnhancedPromptsLibrary()

def get_enhanced_prompt(prompt_id: str, **variables) -> str:
    """Convenience function to get an enhanced prompt"""
    return enhanced_prompts.get_prompt(prompt_id, **variables)

def list_prompt_categories() -> List[str]:
    """List all available prompt categories"""
    return [category.value for category in PromptCategory]

def get_prompts_for_use_case(use_case: str) -> List[str]:
    """Find prompts suitable for a specific use case"""
    matching_prompts = []
    use_case_lower = use_case.lower()
    
    for prompt_id, data in enhanced_prompts.prompts.items():
        prompt_use_case = data.get("use_case", "").lower()
        if use_case_lower in prompt_use_case or prompt_use_case in use_case_lower:
            matching_prompts.append(prompt_id)
    
    return matching_prompts