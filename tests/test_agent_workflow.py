import unittest
import json
from unittest.mock import MagicMock, patch

# Import the agents
from src.agents.agent_base import AgentBase
from src.agents.agent_03_planner import Agent03Planner
from src.agents.agent_04_executor import Agent04Executor
from src.agents.agent_05_designer import Agent05Designer
from src.agents.agent_06_specialist import Agent06Specialist
from src.agents.output_handler import OutputHandler

class TestAgentWorkflow(unittest.TestCase):

    def setUp(self):
        # Initialize agents with mock config paths
        self.agent_base = AgentBase(config_path="mock_config.yaml")
        self.planner = Agent03Planner(config_path="mock_config.yaml")
        self.designer = Agent05Designer(config_path="mock_config.yaml")
        self.executor = Agent04Executor(config_path="mock_config.yaml")
        self.specialist = Agent06Specialist(config_path="mock_config.yaml")
        self.output_handler = OutputHandler(config_path="mock_config.yaml")

        # Mock the BaseAgent's update_status and handle_error methods
        # to prevent actual file operations and allow testing of core logic
        for agent in [self.agent_base, self.planner, self.designer, self.executor, self.specialist, self.output_handler]:
            agent.update_status = MagicMock()
            agent.handle_error = MagicMock(side_effect=lambda e, t: {"status": "error", "message": str(e), "task": t})
            agent.format_response = MagicMock(side_effect=lambda content, type: {"status": "success", "type": type, "content": content})

    def test_todo_app_development_workflow(self):
        print("\n--- Starting Todo App Development Workflow Simulation ---")

        # 1. AgentBase: Initiate Project and Delegate Planning
        print("\n1. AgentBase: Initiating project and delegating planning...")
        initial_task = {
            "task_id": "project_init_001",
            "request": "Develop a simple web-based Todo Application with basic CRUD (Create, Read, Update, Delete) functionality for tasks.",
            "context": {
                "project_type": "software_development",
                "priority": "high",
                "stakeholders": ["Product Owner", "Development Team", "End Users"],
                "initial_scope": "Web application, task management, CRUD operations"
            }
        }
        base_response = self.agent_base.process_task(initial_task)
        self.assertEqual(base_response['status'], 'success')
        self.assertEqual(base_response['type'], 'coordination_plan')
        print(f"   AgentBase Response Type: {base_response['type']}")
        print(f"   AgentBase Content Summary: {base_response['content'].splitlines()[0]}")

        # Simulate extracting planning request from base_response for planner
        # In a real system, AgentBase would parse its own analysis to create the next task
        planner_request_summary = "Create a detailed project plan for a simple web-based Todo Application with basic CRUD functionality."
        
        # 2. Agent03Planner: Create Detailed Project Plan
        print("\n2. Agent03Planner: Creating detailed project plan...")
        planner_task = {
            "task_id": "planning_001",
            "request": planner_request_summary,
            "context": initial_task["context"] # Pass initial context
        }
        planner_response = self.planner.process_task(planner_task)
        self.assertEqual(planner_response['status'], 'success')
        self.assertEqual(planner_response['type'], 'detailed_plan')
        print(f"   Agent03Planner Response Type: {planner_response['type']}")
        print(f"   Agent03Planner Content Summary: {planner_response['content'].splitlines()[0]}")

        # Simulate extracting design request from planner_response for designer
        # In a real system, AgentBase would use the planner's output to formulate the design task
        design_request_summary = "Design the user interface for a simple web-based Todo Application, including views for task list, add task, edit task, and delete/complete task actions."

        # 3. Agent05Designer: Create UI/UX Design
        print("\n3. Agent05Designer: Creating UI/UX design...")
        designer_task = {
            "task_id": "design_001",
            "request": design_request_summary,
            "context": {
                "project_name": "Simple Todo App",
                "design_type": "ui_design",
                "target_audience": "general_public",
                "style_preferences": {"aesthetic": "minimalist", "color_scheme": "modern"},
                "content_requirements": {
                    "text_content": ["Task Title", "Description", "Due Date"],
                    "interactive_elements": ["buttons", "forms", "checkboxes"]
                },
                "technical_specs": {"platform": "web", "format": "html, css"}
            }
        }
        designer_response = self.designer.process_task(designer_task)
        self.assertEqual(designer_response['status'], 'success')
        self.assertEqual(designer_response['type'], 'design_deliverable')
        print(f"   Agent05Designer Response Type: {designer_response['type']}")
        print(f"   Agent05Designer Content Summary: {designer_response['content'].splitlines()[0]}")

        # Simulate extracting implementation request from planner_response and designer_response for executor
        executor_request_summary = "Implement the 'Add Task' feature for the Todo Application. This includes an HTML form, JavaScript logic for submission, and a simulated backend call to add the task."
        
        # 4. Agent04Executor: Implement Core Feature (Add Task)
        print("\n4. Agent04Executor: Implementing 'Add Task' feature...")
        # Mock subprocess.run and requests.post for Executor to avoid actual execution
        with patch('subprocess.run') as mock_subprocess_run, \
             patch('requests.post') as mock_requests_post:
            mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="Simulated script output", stderr="")
            mock_requests_post.return_value = MagicMock(status_code=200, text="Simulated API response")

            executor_task = {
                "task_id": "execution_001",
                "request": executor_request_summary,
                "context": {
                    "project_name": "Simple Todo App",
                    "execution_type": "javascript_script",
                    "dependencies": ["design_001_mockup.html", "design_001_styles.css"],
                    "code_requirements": {
                        "html_form": "<form id='addTaskForm'>...</form>",
                        "javascript_function": "function addTask(taskData) { /* ... */ }",
                        "simulated_api_endpoint": "/api/tasks"
                    }
                }
            }
            executor_response = self.executor.process_task(executor_task)
            self.assertEqual(executor_response['status'], 'success')
            self.assertEqual(executor_response['type'], 'execution_report')
            print(f"   Agent04Executor Response Type: {executor_response['type']}")
            print(f"   Agent04Executor Content Summary: {executor_response['content'].splitlines()[0]}")

        # Simulate extracting security review request for specialist
        specialist_request_summary = "Perform a security review of the 'Add Task' functionality in the Todo Application, specifically checking for XSS and input validation vulnerabilities."

        # 5. Agent06Specialist: Conduct Security Review
        print("\n5. Agent06Specialist: Conducting security review...")
        specialist_task = {
            "task_id": "specialist_001",
            "request": specialist_request_summary,
            "context": {
                "project_name": "Simple Todo App",
                "primary_domain": "security",
                "consultation_type": "review_audit",
                "code_snippet_to_review": "<!-- Simulated HTML/JS code from Executor -->",
                "relevant_data_inputs": ["task title", "task description"]
            }
        }
        specialist_response = self.specialist.process_task(specialist_task)
        self.assertEqual(specialist_response['status'], 'success')
        self.assertEqual(specialist_response['type'], 'specialist_consultation')
        print(f"   Agent06Specialist Response Type: {specialist_response['type']}")
        print(f"   Agent06Specialist Content Summary: {specialist_response['content'].splitlines()[0]}")

        # 6. OutputHandler: Compile Final Report
        print("\n6. OutputHandler: Compiling final report...")
        output_handler_task = {
            "task_id": "final_report_001",
            "request": "Compile a comprehensive final report for the 'Simple Web-based Todo Application' project, integrating outputs from planning, design, implementation, and security review.",
            "context": {
                "project_name": "Simple Todo App",
                "output_format": "comprehensive",
                "planning_completed": True,
                "design_completed": True,
                "execution_completed": True,
                "specialist_consultation": True,
                "agent_contributions": {
                    "planner": self.output_handler._simulate_planner_results(), # Use internal simulation for simplicity
                    "designer": self.output_handler._simulate_designer_results(),
                    "executor": self.output_handler._simulate_executor_results(),
                    "specialist": self.output_handler._simulate_specialist_results()
                }
            }
        }
        output_handler_response = self.output_handler.process_task(output_handler_task)
        self.assertEqual(output_handler_response['status'], 'success')
        self.assertEqual(output_handler_response['type'], 'final_deliverable')
        print(f"   OutputHandler Response Type: {output_handler_response['type']}")
        print(f"   OutputHandler Content Summary: {output_handler_response['content'].splitlines()[0]}")

        print("\n--- Workflow Simulation Complete ---")

if __name__ == '__main__':
    unittest.main()