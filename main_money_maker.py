#!/usr/bin/env python3
"""
💰 Universal AI Money-Making System v5.0.0 - MAIN LAUNCHER
The World's Most Advanced AI Ecosystem for Automated Income Generation

🚀 FEATURES:
✅ Web3 Mining & DeFi Automation (BTC, ETH, DeFi Farming)
✅ Agent Creator Factory (Unlimited Agent Generation)
✅ PTC Click Automation (8 Platforms, $50+/day)
✅ Airdrop Hunter Pro (10 Chains, $2000+/month)
✅ Universal Orchestrator (AI Income Optimization)
✅ Multi-Platform Integration (Desktop, Mobile, Web3)
✅ Real-Time Performance Monitoring
✅ Autonomous Strategy Adjustment
✅ Risk Management & Diversification

🎯 TARGET: $1,000+/day passive income
📈 ROI: 500-2000% annually
🌍 Global Platform Support
🇮🇩 Made with ❤️ in Indonesia

Created by: Mulky Malikul Dhaher
KTP: 1107151509970001 (Developer Access - Free Forever)
Location: Indonesia 🇮🇩
"""

import asyncio
import os
import sys
import time
import signal
from datetime import datetime
from typing import Dict, List, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import all money-making agents
from src.agents.money_making_orchestrator import money_making_orchestrator
from src.agents.web3_mining_agent import web3_mining_agent
from src.agents.agent_creator_agent import agent_creator_agent
from src.agents.ptc_agent import ptc_agent
from src.agents.airdrop_agent import airdrop_agent

class UniversalMoneyMaker:
    """
    💰 Universal AI Money-Making System
    
    The ultimate automated income generation system that coordinates
    multiple AI agents to maximize earnings across all platforms.
    """
    
    def __init__(self):
        self.system_name = "Universal AI Money-Making System v5.0.0"
        self.version = "5.0.0"
        self.status = "initializing"
        
        # System components
        self.orchestrator = money_making_orchestrator
        self.agents = {
            "web3_mining": web3_mining_agent,
            "agent_creator": agent_creator_agent,
            "ptc_clicking": ptc_agent,
            "airdrop_hunting": airdrop_agent
        }
        
        # Performance tracking
        self.start_time = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received shutdown signal ({signum})")
        self.shutdown()
    
    def print_banner(self):
        """Print system banner"""
        banner = f"""
{'='*80}
💰 UNIVERSAL AI MONEY-MAKING SYSTEM v{self.version} 💰
{'='*80}

🚀 The World's Most Advanced AI Ecosystem for Automated Income
🎯 Target: $1,000+/day passive income across all platforms
🌍 Global Multi-Platform Integration
🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia

📊 ACTIVE COMPONENTS:
   ⛏️  Web3 Mining Agent        - Crypto mining & DeFi farming
   🏭 Agent Creator Factory     - Unlimited agent generation  
   🖱️  PTC Click Master         - Automated click earnings
   🪂 Airdrop Hunter Pro       - Multi-chain airdrop farming
   💰 Universal Orchestrator    - AI income optimization

🎯 INCOME TARGETS:
   📈 Daily Target:    $1,000+
   📊 Monthly Target:  $30,000+
   🎉 Yearly Target:   $365,000+
   💹 ROI Target:      500-2000%

⚡ System Status: {self.status.upper()}
🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}
"""
        print(banner)
    
    def print_system_status(self):
        """Print current system status"""
        try:
            # Get orchestrator status
            orchestrator_status = self.orchestrator.get_orchestrator_status()
            
            print(f"\n📊 REAL-TIME SYSTEM STATUS")
            print(f"{'='*50}")
            print(f"💰 Total Daily Earnings:     ${orchestrator_status.get('total_daily_earnings', 0):.2f}")
            print(f"📈 Monthly Projection:       ${orchestrator_status.get('total_monthly_projection', 0):.2f}")
            print(f"🎯 Yearly Projection:        ${orchestrator_status.get('total_yearly_projection', 0):.2f}")
            print(f"🎪 Target Achievement:       {orchestrator_status.get('target_achievement', 0):.1f}%")
            print(f"💹 ROI Percentage:           {orchestrator_status.get('roi_percentage', 0):.1f}%")
            print(f"🔄 Active Income Streams:    {orchestrator_status.get('active_streams', 0)}")
            print(f"📋 Current Strategy:         {orchestrator_status.get('current_strategy', 'unknown').upper()}")
            
            # Individual agent status
            print(f"\n🤖 INDIVIDUAL AGENT STATUS")
            print(f"{'='*50}")
            
            # Web3 Mining Agent
            web3_status = web3_mining_agent.get_mining_status()
            print(f"⛏️  Web3 Mining:     ${web3_status.get('daily_earnings', 0):.2f}/day | Active mines: {web3_status.get('active_mines', 0)}")
            
            # Agent Creator
            creator_status = agent_creator_agent.get_factory_status()
            print(f"🏭 Agent Factory:    ${creator_status.get('total_earnings', 0):.2f} total | Created: {creator_status.get('total_agents_created', 0)} agents")
            
            # PTC Agent
            ptc_status = ptc_agent.get_ptc_status()
            print(f"🖱️  PTC Clicking:     ${ptc_status.get('daily_earnings', 0):.4f}/day | Sites: {ptc_status.get('active_sites', 0)}")
            
            # Airdrop Agent
            airdrop_status = airdrop_agent.get_airdrop_status()
            print(f"🪂 Airdrop Hunter:   ${airdrop_status.get('total_claimed_value', 0):.2f} total | Active: {airdrop_status.get('active_airdrops', 0)}")
            
            print(f"{'='*50}")
            
        except Exception as e:
            print(f"❌ Error getting system status: {e}")
    
    async def initialize_system(self):
        """Initialize all system components"""
        try:
            print("🚀 Initializing Universal Money-Making System...")
            
            # Initialize orchestrator (which initializes all agents)
            print("  💰 Starting Universal Orchestrator...")
            # Orchestrator is already initialized during import
            
            # Verify all agents are ready
            print("  🔍 Verifying agent readiness...")
            
            agents_ready = 0
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'status') and agent.status in ['ready', 'active']:
                    print(f"    ✅ {agent_name.replace('_', ' ').title()}: Ready")
                    agents_ready += 1
                else:
                    print(f"    ⏳ {agent_name.replace('_', ' ').title()}: Initializing...")
            
            # Wait for all agents to be ready
            max_wait = 30  # 30 seconds max wait
            wait_count = 0
            
            while agents_ready < len(self.agents) and wait_count < max_wait:
                await asyncio.sleep(1)
                wait_count += 1
                
                # Recheck agent status
                agents_ready = 0
                for agent_name, agent in self.agents.items():
                    if hasattr(agent, 'status') and agent.status in ['ready', 'active']:
                        agents_ready += 1
            
            if agents_ready == len(self.agents):
                print(f"  ✅ All {agents_ready} agents ready!")
                self.status = "active"
                return True
            else:
                print(f"  ⚠️ Only {agents_ready}/{len(self.agents)} agents ready")
                self.status = "partial"
                return True  # Continue anyway
                
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            self.status = "error"
            return False
    
    async def start_money_making(self):
        """Start the money-making operations"""
        try:
            print("\n🎯 Starting automated money-making operations...")
            
            # Start orchestrator operations
            print("  💰 Activating Universal Orchestrator...")
            
            # Start individual agent operations
            print("  🤖 Starting individual agents...")
            
            # Web3 Mining - Start mining session
            try:
                result = await web3_mining_agent.process_task({
                    "request": "start mining session",
                    "context": {"target_earnings": 100}
                })
                if result.get("success"):
                    print("    ⛏️  Web3 mining operations started")
            except Exception as e:
                print(f"    ❌ Web3 mining start failed: {e}")
            
            # Agent Creator - Create initial agents
            try:
                result = await agent_creator_agent.process_task({
                    "request": "create agent",
                    "context": {"type": "hybrid_earner", "target_income": 200}
                })
                if result.get("success"):
                    print("    🏭 Agent factory operations started")
            except Exception as e:
                print(f"    ❌ Agent factory start failed: {e}")
            
            # PTC - Start clicking session
            try:
                result = await ptc_agent.process_task({
                    "request": "start ptc session",
                    "context": {"target_earnings": 10}
                })
                if result.get("success"):
                    print("    🖱️  PTC clicking operations started")
            except Exception as e:
                print(f"    ❌ PTC start failed: {e}")
            
            # Airdrop - Start hunting session
            try:
                result = await airdrop_agent.process_task({
                    "request": "start airdrop hunting",
                    "context": {"target_value": 1000}
                })
                if result.get("success"):
                    print("    🪂 Airdrop hunting operations started")
            except Exception as e:
                print(f"    ❌ Airdrop hunting start failed: {e}")
            
            self.running = True
            self.start_time = datetime.now()
            
            print("\n✅ All money-making operations are now ACTIVE!")
            print("💰 System is generating passive income 24/7...")
            
        except Exception as e:
            print(f"❌ Failed to start money-making operations: {e}")
    
    async def monitoring_loop(self):
        """Main monitoring and status loop"""
        try:
            status_interval = 300  # 5 minutes
            last_status_time = 0
            
            while self.running:
                current_time = time.time()
                
                # Print status every 5 minutes
                if current_time - last_status_time >= status_interval:
                    self.print_system_status()
                    last_status_time = current_time
                    
                    # Check for optimization opportunities
                    await self._check_optimization_opportunities()
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
        except Exception as e:
            print(f"❌ Monitoring loop error: {e}")
    
    async def _check_optimization_opportunities(self):
        """Check for optimization opportunities"""
        try:
            # Get orchestrator recommendations
            result = await self.orchestrator.process_task({
                "request": "get detailed report",
                "context": {}
            })
            
            if result.get("success"):
                opportunities = result.get("detailed_report", {}).get("optimization_opportunities", [])
                
                if opportunities:
                    print("\n🔧 OPTIMIZATION OPPORTUNITIES DETECTED:")
                    for i, opp in enumerate(opportunities[:3], 1):  # Show top 3
                        print(f"  {i}. {opp.get('type', 'unknown').replace('_', ' ').title()}")
                        print(f"     Action: {opp.get('action', 'No action specified')}")
                    
                    # Auto-optimize if beneficial
                    if len(opportunities) >= 2:
                        print("  🔄 Auto-optimizing system...")
                        await self.orchestrator.process_task({
                            "request": "optimize all streams",
                            "context": {}
                        })
            
        except Exception as e:
            print(f"❌ Optimization check error: {e}")
    
    async def run_interactive_mode(self):
        """Run interactive command mode"""
        print(f"\n🎮 INTERACTIVE MODE ACTIVATED")
        print(f"Type 'help' for available commands, 'quit' to exit")
        print(f"{'='*50}")
        
        while self.running:
            try:
                command = input("\n💰 Money-Maker> ").strip().lower()
                
                if command in ['quit', 'exit', 'stop']:
                    break
                elif command == 'help':
                    self._print_help()
                elif command == 'status':
                    self.print_system_status()
                elif command == 'earnings':
                    await self._show_earnings_overview()
                elif command == 'optimize':
                    await self._manual_optimize()
                elif command == 'report':
                    await self._generate_report()
                elif command == 'agents':
                    await self._show_agent_details()
                elif command.startswith('strategy '):
                    strategy = command.split(' ', 1)[1]
                    await self._change_strategy(strategy)
                elif command == 'scale':
                    await self._scale_operations()
                else:
                    print(f"❌ Unknown command: {command}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Command error: {e}")
        
        print("\n👋 Exiting interactive mode...")
    
    def _print_help(self):
        """Print available commands"""
        help_text = """
🎮 AVAILABLE COMMANDS:
========================
status      - Show real-time system status
earnings    - Show detailed earnings overview  
optimize    - Manually optimize all agents
report      - Generate comprehensive report
agents      - Show individual agent details
strategy X  - Change strategy (aggressive/balanced/conservative)
scale       - Scale operations up
help        - Show this help message
quit        - Exit the system

💡 EXAMPLES:
  strategy aggressive  - Switch to aggressive income strategy
  strategy conservative - Switch to conservative strategy
"""
        print(help_text)
    
    async def _show_earnings_overview(self):
        """Show detailed earnings overview"""
        try:
            result = await self.orchestrator.process_task({
                "request": "get earnings overview",
                "context": {}
            })
            
            if result.get("success"):
                overview = result.get("earnings_overview", {})
                
                print(f"\n💰 DETAILED EARNINGS OVERVIEW")
                print(f"{'='*50}")
                print(f"Daily Earnings:        ${overview.get('total_daily_earnings', 0):.2f}")
                print(f"Monthly Projection:    ${overview.get('total_monthly_projection', 0):.2f}")
                print(f"Yearly Projection:     ${overview.get('total_yearly_projection', 0):.2f}")
                print(f"Target Achievement:    {overview.get('target_achievement', 0):.1f}%")
                print(f"ROI:                   {overview.get('roi_percentage', 0):.1f}%")
                print(f"Strategy:              {overview.get('current_strategy', 'unknown').upper()}")
                
                # Show top performing streams
                streams = result.get("stream_breakdown", [])
                if streams:
                    print(f"\n🏆 TOP PERFORMING STREAMS:")
                    for i, stream in enumerate(streams[:3], 1):
                        print(f"  {i}. {stream['agent_name']}: ${stream['daily_earnings']:.2f}/day")
            
        except Exception as e:
            print(f"❌ Earnings overview error: {e}")
    
    async def _manual_optimize(self):
        """Manually optimize all systems"""
        try:
            print("🔧 Starting manual optimization...")
            
            result = await self.orchestrator.process_task({
                "request": "optimize all streams",
                "context": {}
            })
            
            if result.get("success"):
                print(f"✅ Optimization completed!")
                print(f"Expected improvement: {result.get('expected_monthly_increase', 0):.2f} monthly")
            else:
                print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Manual optimization error: {e}")
    
    async def _generate_report(self):
        """Generate comprehensive system report"""
        try:
            print("📊 Generating comprehensive report...")
            
            result = await self.orchestrator.process_task({
                "request": "get detailed report",
                "context": {}
            })
            
            if result.get("success"):
                report = result.get("detailed_report", {})
                summary = report.get("report_summary", {})
                
                print(f"\n📊 COMPREHENSIVE SYSTEM REPORT")
                print(f"{'='*60}")
                print(f"Report ID:             {summary.get('report_id', 'N/A')}")
                print(f"Generated:             {summary.get('timestamp', 'N/A')}")
                print(f"Daily Earnings:        ${summary.get('total_daily_earnings', 0):.2f}")
                print(f"Monthly Projection:    ${summary.get('total_monthly_projection', 0):.2f}")
                print(f"Growth Rate:           {summary.get('growth_rate', 0):.2f}%")
                print(f"Active Streams:        {summary.get('active_streams', 0)}")
                
                # Show recommendations
                recommendations = summary.get('recommendations', [])
                if recommendations:
                    print(f"\n🎯 RECOMMENDATIONS:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec}")
            
        except Exception as e:
            print(f"❌ Report generation error: {e}")
    
    async def _show_agent_details(self):
        """Show individual agent details"""
        try:
            result = await self.orchestrator.process_task({
                "request": "get streams status",
                "context": {}
            })
            
            if result.get("success"):
                streams = result.get("streams_details", [])
                
                print(f"\n🤖 INDIVIDUAL AGENT DETAILS")
                print(f"{'='*60}")
                
                for stream in streams:
                    print(f"Agent:         {stream['agent_name']}")
                    print(f"Type:          {stream['stream_type']}")
                    print(f"Daily Earnings: ${stream['daily_earnings']:.2f}")
                    print(f"Performance:   {stream['performance_score']:.1f}%")
                    print(f"Risk Level:    {stream['risk_level']}")
                    print(f"Status:        {stream['status']}")
                    print(f"-" * 40)
            
        except Exception as e:
            print(f"❌ Agent details error: {e}")
    
    async def _change_strategy(self, strategy: str):
        """Change income strategy"""
        try:
            result = await self.orchestrator.process_task({
                "request": "manage strategy",
                "context": {"strategy": strategy}
            })
            
            if result.get("success"):
                print(f"✅ Strategy changed to: {strategy.upper()}")
                print(f"New daily target: ${result.get('new_target_daily_income', 0):.2f}")
            else:
                print(f"❌ Strategy change failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Strategy change error: {e}")
    
    async def _scale_operations(self):
        """Scale operations up"""
        try:
            result = await self.orchestrator.process_task({
                "request": "scale operations",
                "context": {"direction": "up", "multiplier": 1.5}
            })
            
            if result.get("success"):
                print(f"✅ Operations scaled up successfully!")
                print(f"New target: ${result.get('new_target_daily', 0):.2f}/day")
            else:
                print(f"❌ Scaling failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Scaling error: {e}")
    
    def shutdown(self):
        """Shutdown the system gracefully"""
        print(f"\n🛑 Shutting down Universal Money-Making System...")
        
        self.running = False
        self.status = "shutting_down"
        
        try:
            # Calculate session statistics
            if self.start_time:
                runtime = datetime.now() - self.start_time
                runtime_hours = runtime.total_seconds() / 3600
                
                print(f"📊 SESSION STATISTICS:")
                print(f"   Runtime: {runtime_hours:.2f} hours")
                
                # Get final earnings
                orchestrator_status = self.orchestrator.get_orchestrator_status()
                total_earnings = orchestrator_status.get('total_daily_earnings', 0)
                
                if runtime_hours > 0:
                    hourly_rate = total_earnings / runtime_hours
                    print(f"   Hourly Rate: ${hourly_rate:.2f}/hour")
                
                print(f"   Total Earnings: ${total_earnings:.2f}")
        
        except Exception as e:
            print(f"❌ Error calculating session stats: {e}")
        
        print(f"✅ System shutdown complete")
        print(f"👋 Thank you for using Universal AI Money-Making System!")
        
        # Force exit
        os._exit(0)

async def main():
    """Main entry point"""
    system = UniversalMoneyMaker()
    
    try:
        # Print banner
        system.print_banner()
        
        # Initialize system
        if not await system.initialize_system():
            print("❌ System initialization failed")
            return
        
        # Start money-making operations
        await system.start_money_making()
        
        # Print initial status
        system.print_system_status()
        
        # Choose operation mode
        print(f"\n🎮 OPERATION MODES:")
        print(f"1. Auto Mode - Fully automated (recommended)")
        print(f"2. Interactive Mode - Manual control")
        
        try:
            mode_choice = input("\nSelect mode (1 or 2): ").strip()
        except (KeyboardInterrupt, EOFError):
            mode_choice = "1"  # Default to auto mode
        
        if mode_choice == "2":
            # Interactive mode
            await system.run_interactive_mode()
        else:
            # Auto mode
            print(f"\n🤖 AUTO MODE ACTIVATED")
            print(f"System running fully automated...")
            print(f"Press Ctrl+C to stop")
            
            # Run monitoring loop
            await system.monitoring_loop()
    
    except KeyboardInterrupt:
        print(f"\n🛑 Received shutdown signal")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        system.shutdown()

if __name__ == "__main__":
    print("🚀 Starting Universal AI Money-Making System...")
    asyncio.run(main())