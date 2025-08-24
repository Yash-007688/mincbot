#!/usr/bin/env python3
"""
Bot Brain Integration Script
This script demonstrates how to integrate the Python BotBrain with your existing Node.js bot system.
It provides a bridge between the intelligent Python brain and the Minecraft bots.
"""

import json
import time
import subprocess
import os
from bot_brain import BotBrain, TaskPriority, BotState

class BotBrainIntegration:
    def __init__(self):
        self.brain = BotBrain()
        self.node_process = None
        self.integration_log = []
        
    def start_node_bots(self):
        """Start the Node.js bot system"""
        try:
            print("Starting Node.js bot system...")
            # Change to the bots directory and start the system
            os.chdir("bots")
            self.node_process = subprocess.Popen(
                ["node", "all_bots.js"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("Node.js bot system started successfully!")
            return True
        except Exception as e:
            print(f"Failed to start Node.js bots: {e}")
            return False
    
    def stop_node_bots(self):
        """Stop the Node.js bot system"""
        if self.node_process:
            print("Stopping Node.js bot system...")
            self.node_process.terminate()
            self.node_process.wait()
            print("Node.js bot system stopped.")
    
    def send_command_to_bots(self, command_data):
        """Send a command to the Node.js bot system"""
        # This would typically use a communication method like:
        # - MQTT
        # - WebSocket
        # - File-based communication
        # - HTTP API
        
        # For now, we'll simulate command sending
        command_json = json.dumps(command_data, indent=2)
        print(f"Sending command to bots: {command_json}")
        
        # Log the command
        self.integration_log.append({
            "timestamp": time.time(),
            "action": "command_sent",
            "data": command_data
        })
        
        return True
    
    def process_user_request(self, user_input):
        """Process user input and generate bot actions"""
        print(f"\nProcessing user request: {user_input}")
        
        # Analyze the request using the bot brain
        analysis = self.brain.analyze_prompt(user_input)
        
        print(f"Intent: {analysis['intent']}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        print(f"Response: {analysis['response']}")
        
        # Generate commands based on the analysis
        commands = self._generate_bot_commands(analysis)
        
        # Send commands to bots
        for command in commands:
            self.send_command_to_bots(command)
        
        return analysis
    
    def _generate_bot_commands(self, analysis):
        """Generate specific bot commands based on analysis"""
        commands = []
        
        intent = analysis['intent']
        entities = analysis['entities']
        actions = analysis['actions']
        
        if intent == "mining":
            # Create mining task
            if entities['bot_names']:
                for bot_name in entities['bot_names']:
                    task_id = self.brain.create_task(
                        task_type="mining",
                        description=f"Mine resources as requested",
                        target_bot=bot_name,
                        parameters={"auto_mining": True},
                        priority=TaskPriority.HIGH
                    )
                    
                    commands.append({
                        "type": "action",
                        "action": "mine",
                        "target": bot_name,
                        "params": {"task_id": task_id, "auto": True}
                    })
        
        elif intent == "building":
            # Create building task
            if entities['bot_names']:
                for bot_name in entities['bot_names']:
                    task_id = self.brain.create_task(
                        task_type="building",
                        description="Build structure as requested",
                        target_bot=bot_name,
                        parameters={"auto_building": True},
                        priority=TaskPriority.MEDIUM
                    )
                    
                    commands.append({
                        "type": "action",
                        "action": "build",
                        "target": bot_name,
                        "params": {"task_id": task_id, "auto": True}
                    })
        
        elif intent == "movement":
            # Handle movement commands
            if entities['locations']:
                for location in entities['locations']:
                    if entities['bot_names']:
                        for bot_name in entities['bot_names']:
                            commands.append({
                                "type": "action",
                                "action": "goto",
                                "target": bot_name,
                                "params": {
                                    "x": location['x'],
                                    "y": location['y'],
                                    "z": location['z']
                                }
                            })
        
        elif intent == "status_request":
            # Get status from all bots
            commands.append({
                "type": "status",
                "action": "get_all",
                "target": "all",
                "params": {}
            })
        
        return commands
    
    def monitor_bot_health(self):
        """Monitor the health and status of all bots"""
        print("\nMonitoring bot health...")
        
        # Get system status
        status = self.brain.get_system_status()
        print(f"Total bots: {status['total_bots']}")
        print(f"Active tasks: {status['active_tasks']}")
        print(f"Idle bots: {status['idle_bots']}")
        print(f"System health: {status['system_health']}")
        
        # Get recommendations for each bot
        for bot_name in self.brain.bots.keys():
            recommendations = self.brain.get_bot_recommendations(bot_name)
            if recommendations:
                print(f"\n{bot_name} recommendations:")
                for rec in recommendations:
                    print(f"  - {rec['action']} (Priority: {rec['priority']})")
    
    def run_interactive_mode(self):
        """Run the bot brain in interactive mode"""
        print("🤖 Bot Brain Interactive Mode")
        print("=" * 40)
        print("Type 'help' for available commands")
        print("Type 'quit' to exit")
        print("=" * 40)
        
        while True:
            try:
                user_input = input("\n🤖 Bot Brain > ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() == 'status':
                    self.monitor_bot_health()
                elif user_input.lower() == 'export':
                    filename = self.brain.export_to_json()
                    print(f"Bot brain state exported to: {filename}")
                elif user_input.lower() == 'optimize':
                    optimizations = self.brain.optimize_work_distribution()
                    if optimizations:
                        print("Work distribution optimizations:")
                        for opt in optimizations:
                            print(f"  - {opt['description']}")
                    else:
                        print("No optimizations needed at this time.")
                elif user_input:
                    # Process the user request
                    self.process_user_request(user_input)
                else:
                    continue
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_help(self):
        """Show available commands"""
        help_text = """
Available Commands:
------------------
help          - Show this help message
status        - Show bot system status
export        - Export bot brain state to JSON
optimize      - Optimize work distribution
quit          - Exit the system

Example Requests:
----------------
"Bot1, mine some iron ore"
"Bot2 and Bot3, build a house at 100 64 200"
"All bots, collect wood"
"Bot1, go to coordinates 150 64 250"
"Show me the status of all bots"
        """
        print(help_text)

def main():
    """Main function to run the bot brain integration"""
    print("🚀 Starting Bot Brain Integration System...")
    
    # Create integration instance
    integration = BotBrainIntegration()
    
    try:
        # Start Node.js bots (optional - comment out if you want to run manually)
        # integration.start_node_bots()
        
        # Run interactive mode
        integration.run_interactive_mode()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Stop Node.js bots if they were started
        integration.stop_node_bots()
        print("✅ Bot Brain Integration System stopped.")

if __name__ == "__main__":
    main()