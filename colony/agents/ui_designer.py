"""
🎨 UI Designer Agent - Autonomous Interface Creation System
AI-powered UI design and component generation

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid
import base64

class UIDesignerAgent:
    """
    Autonomous UI Designer that:
    - Generates React/NextJS components
    - Creates responsive layouts with Tailwind CSS
    - Designs user interfaces from descriptions
    - Builds complete web applications
    - Creates mobile-friendly designs
    - Generates interactive prototypes
    """
    
    def __init__(self, llm_provider=None, dev_engine=None):
        self.agent_id = "ui_designer"
        self.name = "UI Designer Agent"
        self.status = "ready"
        self.capabilities = [
            "ui_design",
            "react_components",
            "tailwind_css",
            "responsive_design",
            "component_library",
            "prototype_creation",
            "design_system"
        ]
        
        # Design templates and patterns
        self.ui_templates = self._load_ui_templates()
        self.component_library = self._initialize_component_library()
        self.design_systems = self._load_design_systems()
        
        # Generated designs tracking
        self.generated_designs: Dict[str, Dict] = {}

        # Set dependencies
        self.llm = llm_provider
        self.dev_engine = dev_engine
        if not self.llm:
            print("⚠️ LLM Gateway not available for UI design")
        if not self.dev_engine:
            print("⚠️ Dev Engine not available for UI design")
        else:
            # Add Next.js template using the dev engine's methods
            self.ui_templates["nextjs_app"] = self._create_nextjs_app_template()
    
    def _load_ui_templates(self) -> Dict[str, Dict]:
        """Load UI templates and patterns"""
        return {
            "dashboard": {
                "description": "Modern dashboard with sidebar and metrics",
                "components": ["navbar", "sidebar", "cards", "charts"],
                "layout": "sidebar-main",
                "complexity": "medium"
            },
            "landing_page": {
                "description": "Marketing landing page with hero section",
                "components": ["hero", "features", "testimonials", "footer"],
                "layout": "single-page",
                "complexity": "simple"
            },
            "ecommerce": {
                "description": "E-commerce product catalog and cart",
                "components": ["product_grid", "filters", "cart", "checkout"],
                "layout": "grid-based",
                "complexity": "complex"
            },
            "blog": {
                "description": "Blog with articles and navigation",
                "components": ["header", "article_list", "sidebar", "pagination"],
                "layout": "content-focused",
                "complexity": "simple"
            },
            "admin_panel": {
                "description": "Admin interface with tables and forms",
                "components": ["data_tables", "forms", "modals", "breadcrumbs"],
                "layout": "admin-layout",
                "complexity": "complex"
            }
        }
    
    def _initialize_component_library(self) -> Dict[str, str]:
        """Initialize reusable component library"""
        return {
            "button": self._get_button_component(),
            "card": self._get_card_component(),
            "navbar": self._get_navbar_component(),
            "sidebar": self._get_sidebar_component(),
            "modal": self._get_modal_component(),
            "form": self._get_form_component(),
            "table": self._get_table_component(),
            "hero": self._get_hero_component()
        }
    
    def _load_design_systems(self) -> Dict[str, Dict]:
        """Load design system configurations"""
        return {
            "modern": {
                "colors": {
                    "primary": "bg-blue-600",
                    "secondary": "bg-gray-600", 
                    "accent": "bg-purple-600",
                    "success": "bg-green-600",
                    "warning": "bg-yellow-600",
                    "error": "bg-red-600"
                },
                "typography": {
                    "heading": "font-bold text-gray-900",
                    "body": "text-gray-700",
                    "caption": "text-sm text-gray-500"
                },
                "spacing": "space-y-6",
                "rounded": "rounded-lg",
                "shadow": "shadow-lg"
            },
            "minimal": {
                "colors": {
                    "primary": "bg-gray-900",
                    "secondary": "bg-gray-100",
                    "accent": "bg-blue-500",
                    "success": "bg-green-500",
                    "warning": "bg-orange-500", 
                    "error": "bg-red-500"
                },
                "typography": {
                    "heading": "font-light text-gray-900",
                    "body": "text-gray-600",
                    "caption": "text-xs text-gray-400"
                },
                "spacing": "space-y-4",
                "rounded": "rounded-none",
                "shadow": "shadow-sm"
            },
            "colorful": {
                "colors": {
                    "primary": "bg-gradient-to-r from-purple-500 to-pink-500",
                    "secondary": "bg-gradient-to-r from-green-400 to-blue-500",
                    "accent": "bg-gradient-to-r from-yellow-400 to-orange-500",
                    "success": "bg-green-400",
                    "warning": "bg-yellow-400",
                    "error": "bg-pink-400"
                },
                "typography": {
                    "heading": "font-bold text-white",
                    "body": "text-gray-800",
                    "caption": "text-sm text-gray-600"
                },
                "spacing": "space-y-8",
                "rounded": "rounded-xl",
                "shadow": "shadow-2xl"
            }
        }
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process UI design task"""
        try:
            action = task.get("action", "create_ui")
            
            if action == "create_ui":
                return await self._create_ui(task)
            elif action == "create_component":
                return await self._create_component(task)
            elif action == "generate_page":
                return await self._generate_page(task)
            elif action == "create_app":
                return await self._create_complete_app(task)
            elif action == "modify_design":
                return await self._modify_design(task)
            elif action == "generate_prototype":
                return await self._generate_prototype(task)
            else:
                return self._create_error_response(f"Unknown action: {action}")
                
        except Exception as e:
            return self._create_error_response(str(e))
    
    async def _create_ui(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create UI based on description"""
        description = task.get("description", "")
        ui_type = task.get("ui_type", "dashboard")
        design_system = task.get("design_system", "modern")
        
        if not description:
            return self._create_error_response("UI description is required")
        
        try:
            # Generate UI using AI if available
            if self.llm:
                ui_code = await self._generate_ui_with_ai(description, ui_type, design_system)
            else:
                ui_code = self._generate_ui_with_template(description, ui_type, design_system)
            
            # Create design ID
            design_id = f"ui_{int(time.time())}_{len(self.generated_designs)}"
            
            # Save design
            design_info = {
                "design_id": design_id,
                "description": description,
                "ui_type": ui_type,
                "design_system": design_system,
                "created_at": datetime.now().isoformat(),
                "code": ui_code,
                "framework": "react",
                "styling": "tailwind"
            }
            
            self.generated_designs[design_id] = design_info
            
            # Save to file
            output_file = f"ui/generated/{design_id}.jsx"
            self._save_ui_to_file(output_file, ui_code)
            
            return {
                "success": True,
                "message": f"UI created successfully",
                "design_id": design_id,
                "design_info": design_info,
                "output_file": output_file,
                "preview_url": f"/preview/{design_id}"
            }
            
        except Exception as e:
            return self._create_error_response(f"Failed to create UI: {str(e)}")
    
    async def _generate_ui_with_ai(self, description: str, ui_type: str, design_system: str) -> str:
        """Generate UI using AI"""
        
        design_config = self.design_systems.get(design_system, self.design_systems["modern"])
        template_info = self.ui_templates.get(ui_type, self.ui_templates["dashboard"])
        
        system_prompt = f"""
        You are an expert React/NextJS UI designer. Create a modern, responsive component based on this description:
        
        Description: {description}
        UI Type: {ui_type}
        Design System: {design_system}
        
        Design System Configuration:
        Colors: {design_config['colors']}
        Typography: {design_config['typography']}
        Spacing: {design_config['spacing']}
        
        Template Information:
        Components needed: {template_info['components']}
        Layout: {template_info['layout']}
        
        Requirements:
        1. Use React functional components with hooks
        2. Use Tailwind CSS for styling (latest classes)
        3. Make it fully responsive (mobile-first)
        4. Include proper accessibility features
        5. Add interactive elements where appropriate
        6. Follow modern React best practices
        7. Include proper TypeScript types if possible
        8. Make it production-ready
        
        Return only the complete React component code, no explanations.
        """
        
        try:
            ui_code = await self.llm.generate_code(
                system_prompt,
                language="jsx",
                model="auto"
            )
            
            # Validate and clean the generated code
            return self._validate_and_clean_ui_code(ui_code)
            
        except Exception as e:
            print(f"AI UI generation failed: {e}")
            # Fallback to template
            return self._generate_ui_with_template(description, ui_type, design_system)
    
    def _generate_ui_with_template(self, description: str, ui_type: str, design_system: str) -> str:
        """Generate UI using templates"""
        
        design_config = self.design_systems.get(design_system, self.design_systems["modern"])
        template_info = self.ui_templates.get(ui_type, self.ui_templates["dashboard"])
        
        component_name = "".join(word.capitalize() for word in description.split()[:3])
        
        # Generate based on UI type
        if ui_type == "dashboard":
            return self._generate_dashboard_template(component_name, design_config)
        elif ui_type == "landing_page":
            return self._generate_landing_page_template(component_name, design_config)
        elif ui_type == "ecommerce":
            return self._generate_ecommerce_template(component_name, design_config)
        else:
            return self._generate_basic_template(component_name, design_config, description)
    
    def _generate_dashboard_template(self, component_name: str, design_config: Dict) -> str:
        """Generate dashboard template"""
        return f"""
import React, {{ useState, useEffect }} from 'react';

const {component_name}Dashboard = () => {{
  const [stats, setStats] = useState({{
    users: 1234,
    revenue: 56789,
    orders: 890,
    growth: 12.5
  }});

  return (
    <div className="min-h-screen bg-gray-50">
      {{/* Header */}}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="{design_config['typography']['heading']} text-2xl">
              {component_name} Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <button className="{design_config['colors']['primary']} text-white px-4 py-2 {design_config['rounded']} hover:opacity-90">
                New Item
              </button>
            </div>
          </div>
        </div>
      </header>

      {{/* Main Content */}}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {{/* Stats Cards */}}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 {design_config['rounded']} {design_config['shadow']}">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="{design_config['colors']['primary']} w-8 h-8 {design_config['rounded']} flex items-center justify-center">
                  <span className="text-white font-bold">U</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="{design_config['typography']['caption']}">Total Users</p>
                <p className="{design_config['typography']['heading']} text-2xl">{{stats.users.toLocaleString()}}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 {design_config['rounded']} {design_config['shadow']}">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="{design_config['colors']['success']} w-8 h-8 {design_config['rounded']} flex items-center justify-center">
                  <span className="text-white font-bold">$</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="{design_config['typography']['caption']}">Revenue</p>
                <p className="{design_config['typography']['heading']} text-2xl">${{stats.revenue.toLocaleString()}}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 {design_config['rounded']} {design_config['shadow']}">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="{design_config['colors']['accent']} w-8 h-8 {design_config['rounded']} flex items-center justify-center">
                  <span className="text-white font-bold">O</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="{design_config['typography']['caption']}">Orders</p>
                <p className="{design_config['typography']['heading']} text-2xl">{{stats.orders.toLocaleString()}}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 {design_config['rounded']} {design_config['shadow']}">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="{design_config['colors']['warning']} w-8 h-8 {design_config['rounded']} flex items-center justify-center">
                  <span className="text-white font-bold">%</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="{design_config['typography']['caption']}">Growth</p>
                <p className="{design_config['typography']['heading']} text-2xl">+{{stats.growth}}%</p>
              </div>
            </div>
          </div>
        </div>

        {{/* Content Areas */}}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 {design_config['rounded']} {design_config['shadow']}">
            <h3 className="{design_config['typography']['heading']} text-lg mb-4">Recent Activity</h3>
            <div className="{design_config['spacing']}">
              <div className="flex items-center py-2">
                <div className="w-2 h-2 {design_config['colors']['primary']} rounded-full mr-3"></div>
                <span className="{design_config['typography']['body']}">New user registered</span>
              </div>
              <div className="flex items-center py-2">
                <div className="w-2 h-2 {design_config['colors']['success']} rounded-full mr-3"></div>
                <span className="{design_config['typography']['body']}">Payment received</span>
              </div>
              <div className="flex items-center py-2">
                <div className="w-2 h-2 {design_config['colors']['warning']} rounded-full mr-3"></div>
                <span className="{design_config['typography']['body']}">System maintenance</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 {design_config['rounded']} {design_config['shadow']}">
            <h3 className="{design_config['typography']['heading']} text-lg mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-4">
              <button className="{design_config['colors']['primary']} text-white p-4 {design_config['rounded']} hover:opacity-90 transition-opacity">
                Add User
              </button>
              <button className="{design_config['colors']['secondary']} text-white p-4 {design_config['rounded']} hover:opacity-90 transition-opacity">
                Generate Report
              </button>
              <button className="{design_config['colors']['accent']} text-white p-4 {design_config['rounded']} hover:opacity-90 transition-opacity">
                Send Message
              </button>
              <button className="{design_config['colors']['success']} text-white p-4 {design_config['rounded']} hover:opacity-90 transition-opacity">
                Export Data
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}};

export default {component_name}Dashboard;
"""
    
    def _generate_landing_page_template(self, component_name: str, design_config: Dict) -> str:
        """Generate landing page template"""
        return f"""
import React from 'react';

const {component_name}Landing = () => {{
  return (
    <div className="min-h-screen bg-white">
      {{/* Hero Section */}}
      <section className="{design_config['colors']['primary']} text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Welcome to {component_name}
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-opacity-90">
              The ultimate solution for your business needs
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-gray-900 px-8 py-3 {design_config['rounded']} font-semibold hover:bg-gray-100 transition-colors">
                Get Started
              </button>
              <button className="border-2 border-white text-white px-8 py-3 {design_config['rounded']} font-semibold hover:bg-white hover:text-gray-900 transition-colors">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </section>

      {{/* Features Section */}}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="{design_config['typography']['heading']} text-3xl md:text-4xl mb-4">
              Amazing Features
            </h2>
            <p className="{design_config['typography']['body']} text-lg">
              Everything you need to succeed
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="{design_config['colors']['primary']} w-16 h-16 {design_config['rounded']} mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">1</span>
              </div>
              <h3 className="{design_config['typography']['heading']} text-xl mb-2">Fast & Reliable</h3>
              <p className="{design_config['typography']['body']}">Lightning fast performance with 99.9% uptime guarantee</p>
            </div>
            
            <div className="text-center p-6">
              <div className="{design_config['colors']['accent']} w-16 h-16 {design_config['rounded']} mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">2</span>
              </div>
              <h3 className="{design_config['typography']['heading']} text-xl mb-2">Easy to Use</h3>
              <p className="{design_config['typography']['body']}">Intuitive interface designed for everyone</p>
            </div>
            
            <div className="text-center p-6">
              <div className="{design_config['colors']['success']} w-16 h-16 {design_config['rounded']} mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">3</span>
              </div>
              <h3 className="{design_config['typography']['heading']} text-xl mb-2">Secure</h3>
              <p className="{design_config['typography']['body']}">Enterprise-grade security for your peace of mind</p>
            </div>
          </div>
        </div>
      </section>

      {{/* CTA Section */}}
      <section className="py-24">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="{design_config['typography']['heading']} text-3xl md:text-4xl mb-4">
            Ready to Get Started?
          </h2>
          <p className="{design_config['typography']['body']} text-lg mb-8">
            Join thousands of satisfied customers today
          </p>
          <button className="{design_config['colors']['primary']} text-white px-8 py-4 {design_config['rounded']} text-lg font-semibold hover:opacity-90 transition-opacity">
            Start Your Free Trial
          </button>
        </div>
      </section>

      {{/* Footer */}}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">{component_name}</h3>
            <p className="text-gray-400">© 2024 All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}};

export default {component_name}Landing;
"""
    
    def _generate_basic_template(self, component_name: str, design_config: Dict, description: str) -> str:
        """Generate basic template"""
        return f"""
import React, {{ useState }} from 'react';

const {component_name}Component = () => {{
  const [data, setData] = useState([]);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white {design_config['rounded']} {design_config['shadow']} p-8">
        <h1 className="{design_config['typography']['heading']} text-3xl mb-6">
          {component_name}
        </h1>
        
        <p className="{design_config['typography']['body']} mb-6">
          {description}
        </p>
        
        <div className="flex gap-4">
          <button className="{design_config['colors']['primary']} text-white px-6 py-2 {design_config['rounded']} hover:opacity-90 transition-opacity">
            Primary Action
          </button>
          <button className="{design_config['colors']['secondary']} text-white px-6 py-2 {design_config['rounded']} hover:opacity-90 transition-opacity">
            Secondary Action
          </button>
        </div>
      </div>
    </div>
  );
}};

export default {component_name}Component;
"""
    
    def _validate_and_clean_ui_code(self, code: str) -> str:
        """Validate and clean generated UI code"""
        # Remove any markdown code blocks
        if "```" in code:
            parts = code.split("```")
            for i, part in enumerate(parts):
                if part.startswith("jsx") or part.startswith("react"):
                    code = parts[i+1] if i+1 < len(parts) else part
                    break
        
        # Ensure it's valid React component structure
        if "import React" not in code:
            code = "import React from 'react';\n\n" + code
        
        if "export default" not in code:
            # Try to find component name and add export
            lines = code.split('\n')
            for line in lines:
                if "const " in line and "= () => {" in line:
                    component_name = line.split("const ")[1].split(" =")[0]
                    code += f"\n\nexport default {component_name};"
                    break
        
        return code
    
    def _save_ui_to_file(self, file_path: str, content: str):
        """Save UI code to file"""
        try:
            file_obj = Path(file_path)
            file_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_obj, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Failed to save UI file: {e}")
    
    async def _create_component(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a specific React component"""
        component_name = task.get("component_name", "")
        component_type = task.get("component_type", "button")
        props = task.get("props", {})
        
        if not component_name:
            return self._create_error_response("Component name is required")
        
        # Get component from library or generate new one
        if component_type in self.component_library:
            base_component = self.component_library[component_type]
            # Customize with props
            component_code = self._customize_component(base_component, component_name, props)
        else:
            # Generate new component
            component_code = await self._generate_custom_component(component_name, component_type, props)
        
        return {
            "success": True,
            "component_name": component_name,
            "component_type": component_type,
            "code": component_code,
            "props": props
        }
    
    def _get_button_component(self) -> str:
        """Get button component template"""
        return """
import React from 'react';

const CustomButton = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  onClick,
  className = '' 
}) => {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white'
  };
  
  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };
  
  return (
    <button
      className={`${variants[variant]} ${sizes[size]} rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export default CustomButton;
"""
    
    def _get_card_component(self) -> str:
        """Get card component template"""
        return """
import React from 'react';

const CustomCard = ({ 
  children, 
  title, 
  subtitle, 
  image, 
  actions, 
  className = '' 
}) => {
  return (
    <div className={`bg-white rounded-lg shadow-lg overflow-hidden ${className}`}>
      {image && (
        <div className="h-48 bg-gray-200">
          <img src={image} alt={title} className="w-full h-full object-cover" />
        </div>
      )}
      
      <div className="p-6">
        {title && (
          <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        )}
        
        {subtitle && (
          <p className="text-gray-600 mb-4">{subtitle}</p>
        )}
        
        <div className="text-gray-700">
          {children}
        </div>
        
        {actions && (
          <div className="mt-6 flex gap-2">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomCard;
"""
    
    def _get_navbar_component(self) -> str:
        """Get navbar component template"""
        return """
import React, { useState } from 'react';

const CustomNavbar = ({ 
  brand, 
  links = [], 
  actions, 
  className = '' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <nav className={`bg-white shadow-lg ${className}`}>
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <span className="text-xl font-bold text-gray-900">{brand}</span>
          </div>
          
          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {links.map((link, index) => (
              <a
                key={index}
                href={link.href}
                className="text-gray-700 hover:text-blue-600 transition-colors"
              >
                {link.label}
              </a>
            ))}
            
            {actions && (
              <div className="flex gap-2">
                {actions}
              </div>
            )}
          </div>
          
          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
        
        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4">
            {links.map((link, index) => (
              <a
                key={index}
                href={link.href}
                className="block py-2 text-gray-700 hover:text-blue-600"
              >
                {link.label}
              </a>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
};

export default CustomNavbar;
"""
    
<<<<<<< HEAD:colony/agents/ui_designer.py
    def _get_form_component(self) -> str:
        """Get form component template"""
        return """
import React, { useState } from 'react';

const CustomForm = ({ 
  onSubmit, 
  fields = [], 
  submitText = 'Submit',
  className = '' 
}) => {
  const [formData, setFormData] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSubmit) onSubmit(formData);
  };

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-4 ${className}`}>
      {fields.map((field, index) => (
        <div key={index}>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {field.label}
          </label>
          {field.type === 'textarea' ? (
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={field.placeholder}
              onChange={(e) => handleChange(field.name, e.target.value)}
            />
          ) : (
            <input
              type={field.type || 'text'}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={field.placeholder}
              onChange={(e) => handleChange(field.name, e.target.value)}
            />
          )}
        </div>
      ))}
      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
      >
        {submitText}
      </button>
    </form>
  );
};

export default CustomForm;
"""

=======
>>>>>>> origin/feature/system-refactor-and-ui-update:agents/ui_designer.py
    def _get_table_component(self) -> str:
        """Get table component template"""
        return """
import React from 'react';

<<<<<<< HEAD:colony/agents/ui_designer.py
const CustomTable = ({ 
  columns = [], 
  data = [], 
  className = '' 
}) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column, index) => (
              <th
                key={index}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {column.header}
=======
const CustomTable = ({ columns = [], data = [], className = '' }) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full bg-white">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col, index) => (
              <th key={index} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {col.header}
>>>>>>> origin/feature/system-refactor-and-ui-update:agents/ui_designer.py
              </th>
            ))}
          </tr>
        </thead>
<<<<<<< HEAD:colony/agents/ui_designer.py
        <tbody className="divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-gray-50">
              {columns.map((column, colIndex) => (
                <td
                  key={colIndex}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                >
                  {row[column.accessor]}
=======
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((col, colIndex) => (
                <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {row[col.accessor]}
>>>>>>> origin/feature/system-refactor-and-ui-update:agents/ui_designer.py
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CustomTable;
"""

<<<<<<< HEAD:colony/agents/ui_designer.py
=======
    def _get_form_component(self) -> str:
        """Get form component template"""
        return """
import React from 'react';

const CustomForm = ({ fields = [], onSubmit, className = '' }) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-4 ${className}`}>
      {fields.map((field, index) => (
        <div key={index}>
          <label htmlFor={field.name} className="block text-sm font-medium text-gray-700">
            {field.label}
          </label>
          <input
            type={field.type || 'text'}
            name={field.name}
            id={field.name}
            placeholder={field.placeholder}
            required={field.required}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
      ))}
      <button
        type="submit"
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Submit
      </button>
    </form>
  );
};

export default CustomForm;
"""

    def _get_modal_component(self) -> str:
        """Get modal component template"""
        return """
import React from 'react';

const CustomModal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">{title}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">&times;</button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
};

export default CustomModal;
"""

    def _get_sidebar_component(self) -> str:
        """Get sidebar component template"""
        return """
import React, { useState } from 'react';

const CustomSidebar = ({ links = [], className = '' }) => {
  return (
    <aside className={`bg-gray-800 text-white w-64 min-h-screen p-4 ${className}`}>
      <div className="mb-8">
        <h2 className="text-2xl font-bold">Dashboard</h2>
      </div>
      <nav>
        <ul>
          {links.map((link, index) => (
            <li key={index} className="mb-4">
              <a
                href={link.href}
                className="flex items-center p-2 rounded-lg hover:bg-gray-700 transition-colors"
              >
                <span className="mr-3">{link.icon}</span>
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default CustomSidebar;
"""

>>>>>>> origin/feature/system-refactor-and-ui-update:agents/ui_designer.py
    def _get_hero_component(self) -> str:
        """Get hero section component"""
        return """
import React from 'react';

const HeroSection = ({ 
  title, 
  subtitle, 
  backgroundImage, 
  primaryAction, 
  secondaryAction,
  className = '' 
}) => {
  return (
    <section 
      className={`relative bg-gradient-to-r from-blue-600 to-purple-600 text-white py-24 ${className}`}
      style={backgroundImage ? { backgroundImage: `url(${backgroundImage})` } : {}}
    >
      <div className="absolute inset-0 bg-black bg-opacity-50"></div>
      
      <div className="relative max-w-7xl mx-auto px-4 text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          {title}
        </h1>
        
        {subtitle && (
          <p className="text-xl md:text-2xl mb-8 text-opacity-90">
            {subtitle}
          </p>
        )}
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {primaryAction}
          {secondaryAction}
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
"""
    
    def _get_modal_component(self) -> str:
        """Get modal component for agent dialogs"""
        return """
import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const AgentModal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
      
      <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AgentModal;
"""

    def _get_sidebar_component(self) -> str:
        """Get sidebar component for agent control dashboard"""
        return """
import React, { useState } from 'react';
import { ChevronDownIcon, ChevronRightIcon, CpuChipIcon, PlayIcon, PauseIcon, StopIcon } from '@heroicons/react/24/outline';

const AgentSidebar = ({ agents, onAgentSelect, onAgentAction, selectedAgent }) => {
  const [expandedGroups, setExpandedGroups] = useState({
    'security': true,
    'development': true,
    'business': true,
    'system': true
  });

  const agentGroups = {
    security: ['commander_agi', 'bug_hunter', 'authentication'],
    development: ['dev_engine', 'fullstack_dev', 'ui_designer'],
    business: ['money_maker', 'marketing', 'quality_control'],
    system: ['backup_colony', 'knowledge_manager', 'data_sync']
  };

  const toggleGroup = (group) => {
    setExpandedGroups(prev => ({
      ...prev,
      [group]: !prev[group]
    }));
  };

  const getAgentStatus = (agentId) => {
    const agent = agents[agentId];
    if (!agent) return 'offline';
    return agent.status || 'unknown';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-500';
      case 'running': return 'text-blue-500';
      case 'error': return 'text-red-500';
      case 'paused': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="w-80 bg-gray-900 text-white h-full overflow-y-auto">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center">
          <CpuChipIcon className="w-6 h-6 mr-2" />
          Agent Control Center
        </h2>
      </div>

      <div className="p-4">
        {Object.entries(agentGroups).map(([groupName, agentIds]) => (
          <div key={groupName} className="mb-4">
            <button
              onClick={() => toggleGroup(groupName)}
              className="flex items-center w-full text-left text-gray-300 hover:text-white mb-2"
            >
              {expandedGroups[groupName] ? (
                <ChevronDownIcon className="w-4 h-4 mr-2" />
              ) : (
                <ChevronRightIcon className="w-4 h-4 mr-2" />
              )}
              <span className="font-medium capitalize">{groupName}</span>
            </button>

            {expandedGroups[groupName] && (
              <div className="ml-6 space-y-2">
                {agentIds.map(agentId => {
                  const agent = agents[agentId];
                  const status = getAgentStatus(agentId);
                  const isSelected = selectedAgent === agentId;

                  return (
                    <div
                      key={agentId}
                      className={`p-2 rounded cursor-pointer border ${
                        isSelected 
                          ? 'bg-blue-600 border-blue-500' 
                          : 'bg-gray-800 border-gray-700 hover:bg-gray-700'
                      }`}
                      onClick={() => onAgentSelect(agentId)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className={`w-3 h-3 rounded-full ${getStatusColor(status)} mr-2`} />
                          <span className="text-sm">{agent?.name || agentId}</span>
                        </div>
                        <div className="flex space-x-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onAgentAction(agentId, 'start');
                            }}
                            className="p-1 hover:bg-green-600 rounded"
                            title="Start Agent"
                          >
                            <PlayIcon className="w-3 h-3" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onAgentAction(agentId, 'pause');
                            }}
                            className="p-1 hover:bg-yellow-600 rounded"
                            title="Pause Agent"
                          >
                            <PauseIcon className="w-3 h-3" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onAgentAction(agentId, 'stop');
                            }}
                            className="p-1 hover:bg-red-600 rounded"
                            title="Stop Agent"
                          >
                            <StopIcon className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        Status: {status}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentSidebar;
"""

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": error_message,
            "agent": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }

    def _create_nextjs_app_template(self) -> Dict:
        """
        Creates a Next.js app template structure by borrowing from DevEngineAgent.
        """
        if not self.dev_engine:
            return {}
            
        template = self.dev_engine.project_templates.get("nextjs_app", {})
        return {
            "description": template.get("description", "Next.js application"),
            "components": ["layout", "page", "globals.css"],
            "layout": "app-router",
            "complexity": "medium",
            "files": template.get("files", {})
        }

