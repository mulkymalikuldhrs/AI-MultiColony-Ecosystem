#!/usr/bin/env python3
"""
🐪 Camel AI Agent Integration v7.0.0
Advanced multi-agent collaboration system using Camel AI

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from connectors.llm_gateway import llm_gateway

class CamelAgent:
    """
    Camel AI Agent - Multi-Agent Collaborative Intelligence
    Implements collaborative problem-solving with multiple agent personalities
    """
    
    def __init__(self, agent_id: str = "camel_agent", llm_provider=None):
        self.agent_id = agent_id
        self.name = "Camel AI Collaborative Agent"
        self.status = "initializing"
        self.llm_provider = llm_provider or llm_gateway
        
        # Owner identification
        self.owner_identity = "1108151509970001"  # Mulky Malikul Dhaher
        self.owner_name = "Mulky Malikul Dhaher"
        
        # Camel AI specific capabilities
        self.capabilities = [
            "multi_agent_collaboration",
            "role_playing_conversations",
            "consensus_building",
            "collaborative_problem_solving",
            "agent_coordination",
            "task_decomposition",
            "collective_intelligence"
        ]
        
        # Agent roles for collaboration
        self.agent_roles = {
            "task_analyst": {
                "description": "Analyzes and breaks down complex tasks",
                "specialty": "Task decomposition and analysis",
                "personality": "Analytical, methodical, detail-oriented"
            },
            "solution_architect": {
                "description": "Designs optimal solutions and approaches",
                "specialty": "Solution design and architecture",
                "personality": "Strategic, innovative, big-picture thinking"
            },
            "implementation_expert": {
                "description": "Focuses on practical implementation details",
                "specialty": "Technical implementation and execution",
                "personality": "Practical, hands-on, results-oriented"
            },
            "quality_reviewer": {
                "description": "Reviews and validates solutions",
                "specialty": "Quality assurance and validation",
                "personality": "Critical, thorough, quality-focused"
            },
            "coordinator": {
                "description": "Coordinates collaboration between agents",
                "specialty": "Agent coordination and consensus building",
                "personality": "Diplomatic, organized, collaborative"
            }
        }
        
        # Collaboration state
        self.active_collaborations = {}
        self.collaboration_history = []
        
        print(f"🐪 {self.name} initialized")
        print(f"👑 Absolute loyalty to: {self.owner_name} ({self.owner_identity})")
        print(f"🤝 Collaborative capabilities: {len(self.capabilities)} active")
        
        self.status = "ready"
    
    async def process_task(self, task_data: Dict) -> Dict:
        """Process task using multi-agent collaboration"""
        task_id = task_data.get('task_id', f"task_{int(time.time())}")
        task_content = task_data.get('content', '')
        complexity = task_data.get('complexity', 'medium')
        
        print(f"🐪 Starting collaborative task processing: {task_id}")
        
        try:
            # Initialize collaboration session
            collaboration_session = await self._initialize_collaboration(task_id, task_content, complexity)
            
            # Multi-agent collaboration process
            result = await self._run_multi_agent_collaboration(collaboration_session)
            
            # Finalize and validate result
            final_result = await self._finalize_collaboration(collaboration_session, result)
            
            return {
                'success': True,
                'task_id': task_id,
                'result': final_result,
                'collaboration_summary': collaboration_session['summary'],
                'agents_involved': list(collaboration_session['agents'].keys()),
                'processing_time': time.time() - collaboration_session['start_time']
            }
            
        except Exception as e:
            print(f"🔥 Camel collaboration error: {e}")
            return {
                'success': False,
                'task_id': task_id,
                'error': str(e),
                'fallback_result': await self._fallback_processing(task_content)
            }
    
    async def _initialize_collaboration(self, task_id: str, task_content: str, complexity: str) -> Dict:
        """Initialize a collaboration session"""
        
        # Determine which agents to involve based on complexity
        if complexity == 'simple':
            involved_agents = ['solution_architect', 'implementation_expert']
        elif complexity == 'medium':
            involved_agents = ['task_analyst', 'solution_architect', 'implementation_expert']
        else:  # complex
            involved_agents = list(self.agent_roles.keys())
        
        collaboration_session = {
            'session_id': task_id,
            'task_content': task_content,
            'complexity': complexity,
            'agents': {role: self.agent_roles[role] for role in involved_agents},
            'start_time': time.time(),
            'conversation_log': [],
            'decisions': [],
            'status': 'active'
        }
        
        self.active_collaborations[task_id] = collaboration_session
        
        print(f"🤝 Collaboration session initialized with {len(involved_agents)} agents")
        return collaboration_session
    
    async def _run_multi_agent_collaboration(self, session: Dict) -> Dict:
        """Run the multi-agent collaboration process"""
        
        task_content = session['task_content']
        agents = session['agents']
        
        print(f"🎭 Starting multi-agent conversation...")
        
        # Phase 1: Task Analysis
        analysis_results = []
        for agent_role, agent_info in agents.items():
            if agent_role in ['task_analyst', 'coordinator']:
                analysis = await self._agent_analyze_task(agent_role, agent_info, task_content)
                analysis_results.append(analysis)
                session['conversation_log'].append({
                    'agent': agent_role,
                    'phase': 'analysis',
                    'content': analysis,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Phase 2: Solution Design
        design_results = []
        for agent_role, agent_info in agents.items():
            if agent_role in ['solution_architect', 'implementation_expert']:
                design = await self._agent_design_solution(agent_role, agent_info, task_content, analysis_results)
                design_results.append(design)
                session['conversation_log'].append({
                    'agent': agent_role,
                    'phase': 'design',
                    'content': design,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Phase 3: Consensus Building
        if len(agents) > 2:
            consensus = await self._build_consensus(agents, analysis_results, design_results)
            session['conversation_log'].append({
                'agent': 'coordinator',
                'phase': 'consensus',
                'content': consensus,
                'timestamp': datetime.now().isoformat()
            })
        else:
            consensus = design_results[0] if design_results else analysis_results[0]
        
        # Phase 4: Quality Review
        if 'quality_reviewer' in agents:
            review = await self._quality_review(task_content, consensus)
            session['conversation_log'].append({
                'agent': 'quality_reviewer',
                'phase': 'review',
                'content': review,
                'timestamp': datetime.now().isoformat()
            })
            
            # Apply review feedback
            final_result = await self._apply_review_feedback(consensus, review)
        else:
            final_result = consensus
        
        return final_result
    
    async def _agent_analyze_task(self, agent_role: str, agent_info: Dict, task_content: str) -> str:
        """Have a specific agent analyze the task"""
        
        prompt = f"""
You are acting as a {agent_role} in a collaborative AI team.

Your role: {agent_info['description']}
Your specialty: {agent_info['specialty']}
Your personality: {agent_info['personality']}

Task to analyze: {task_content}

Please provide your analysis from your specific perspective and expertise.
Focus on what aspects are most important from your role's viewpoint.
Be concise but thorough.
"""
        
        try:
            response = await self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            if response.get('success'):
                return response['content']
            else:
                return f"[{agent_role}] Basic analysis: {task_content[:100]}..."
                
        except Exception as e:
            return f"[{agent_role}] Analysis unavailable due to: {str(e)}"
    
    async def _agent_design_solution(self, agent_role: str, agent_info: Dict, task_content: str, analyses: List[str]) -> str:
        """Have a specific agent design a solution"""
        
        analysis_summary = "\n".join([f"- {analysis[:200]}..." for analysis in analyses])
        
        prompt = f"""
You are acting as a {agent_role} in a collaborative AI team.

Your role: {agent_info['description']}
Your specialty: {agent_info['specialty']}
Your personality: {agent_info['personality']}

Original task: {task_content}

Team analysis summary:
{analysis_summary}

Based on the team's analysis, please design a solution from your perspective.
Focus on the practical aspects that align with your specialty.
Be specific and actionable.
"""
        
        try:
            response = await self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.6
            )
            
            if response.get('success'):
                return response['content']
            else:
                return f"[{agent_role}] Basic solution approach for: {task_content[:100]}..."
                
        except Exception as e:
            return f"[{agent_role}] Solution design unavailable due to: {str(e)}"
    
    async def _build_consensus(self, agents: Dict, analyses: List[str], designs: List[str]) -> str:
        """Build consensus among multiple agent perspectives"""
        
        all_inputs = analyses + designs
        inputs_summary = "\n".join([f"- {inp[:150]}..." for inp in all_inputs])
        
        prompt = f"""
You are acting as a coordinator in a collaborative AI team.
Your job is to synthesize multiple perspectives into a coherent consensus solution.

Team perspectives summary:
{inputs_summary}

Please create a unified solution that:
1. Incorporates the best ideas from all team members
2. Resolves any conflicts between different approaches
3. Provides a clear, actionable plan
4. Maintains the collaborative spirit of the team

Focus on building consensus rather than choosing sides.
"""
        
        try:
            response = await self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.5
            )
            
            if response.get('success'):
                return response['content']
            else:
                return f"Consensus solution combining {len(all_inputs)} perspectives"
                
        except Exception as e:
            return f"Consensus building failed: {str(e)}, using first design: {designs[0] if designs else 'No design available'}"
    
    async def _quality_review(self, original_task: str, proposed_solution: str) -> str:
        """Perform quality review of the proposed solution"""
        
        prompt = f"""
You are acting as a quality reviewer in a collaborative AI team.
Your job is to critically evaluate the proposed solution.

Original task: {original_task}

Proposed solution: {proposed_solution}

Please provide a thorough quality review that evaluates:
1. How well the solution addresses the original task
2. Potential issues or gaps in the solution
3. Suggestions for improvement
4. Overall quality assessment

Be constructive but critical. Focus on making the solution better.
"""
        
        try:
            response = await self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.4
            )
            
            if response.get('success'):
                return response['content']
            else:
                return "Quality review: Solution appears adequate for the given task."
                
        except Exception as e:
            return f"Quality review unavailable: {str(e)}"
    
    async def _apply_review_feedback(self, original_solution: str, review_feedback: str) -> str:
        """Apply review feedback to improve the solution"""
        
        prompt = f"""
You are refining a solution based on quality review feedback.

Original solution: {original_solution}

Quality review feedback: {review_feedback}

Please provide an improved version of the solution that addresses the feedback.
Keep what works well and improve what needs attention.
"""
        
        try:
            response = await self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.5
            )
            
            if response.get('success'):
                return response['content']
            else:
                return original_solution  # Fall back to original if refinement fails
                
        except Exception as e:
            return original_solution
    
    async def _finalize_collaboration(self, session: Dict, result: str) -> Dict:
        """Finalize the collaboration session"""
        
        session['end_time'] = time.time()
        session['status'] = 'completed'
        session['final_result'] = result
        
        # Create summary
        session['summary'] = {
            'agents_count': len(session['agents']),
            'conversation_turns': len(session['conversation_log']),
            'processing_time': session['end_time'] - session['start_time'],
            'complexity': session['complexity'],
            'success': True
        }
        
        # Save to history
        self.collaboration_history.append(session)
        
        # Remove from active
        if session['session_id'] in self.active_collaborations:
            del self.active_collaborations[session['session_id']]
        
        return {
            'solution': result,
            'collaboration_metadata': session['summary'],
            'conversation_log': session['conversation_log'][-3:],  # Last 3 entries
            'agents_involved': list(session['agents'].keys())
        }
    
    async def _fallback_processing(self, task_content: str) -> str:
        """Fallback processing when collaboration fails"""
        return f"🐪 Camel AI Fallback: Processed task - {task_content[:100]}... (Collaboration system temporarily unavailable)"
    
    def get_collaboration_stats(self) -> Dict:
        """Get collaboration statistics"""
        return {
            'active_collaborations': len(self.active_collaborations),
            'total_collaborations': len(self.collaboration_history),
            'available_agent_roles': list(self.agent_roles.keys()),
            'capabilities': self.capabilities,
            'status': self.status
        }
    
    async def start_collaborative_session(self, participants: List[str], topic: str) -> str:
        """Start a new collaborative session"""
        session_id = f"collab_{int(time.time())}"
        
        task_data = {
            'task_id': session_id,
            'content': f"Collaborative discussion on: {topic}",
            'complexity': 'medium',
            'participants': participants
        }
        
        result = await self.process_task(task_data)
        return session_id if result['success'] else None

# Create global instance
camel_agent = CamelAgent()

# Test function
async def test_camel_agent():
    """Test the Camel Agent"""
    print("\n🧪 Testing Camel AI Agent...")
    
    test_task = {
        'task_id': 'test_collaboration',
        'content': 'Design a user-friendly mobile app for task management',
        'complexity': 'complex'
    }
    
    result = await camel_agent.process_task(test_task)
    print(f"\nCollaboration Result: {json.dumps(result, indent=2)}")
    
    stats = camel_agent.get_collaboration_stats()
    print(f"\nCollaboration Stats: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_camel_agent())