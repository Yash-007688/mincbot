#!/usr/bin/env python3
"""
Bot Vision Web Interface - Web-based Bot Vision and Command System
This provides a web dashboard for monitoring bot vision and giving live commands.
Access it through your web browser for a visual command center experience!
"""

import json
import time
import threading
import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import math
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from bot_brain import BotBrain, TaskPriority, BotState

# Web interface HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Bot Vision Commander - Web Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .panel h2 {
            margin-bottom: 15px;
            color: #4CAF50;
            font-size: 1.5em;
        }
        
        .bot-grid {
            display: grid;
            gap: 10px;
        }
        
        .bot-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #4CAF50;
        }
        
        .bot-card.critical {
            border-left-color: #f44336;
            background: rgba(244, 67, 54, 0.2);
        }
        
        .bot-card.warning {
            border-left-color: #ff9800;
            background: rgba(255, 152, 0, 0.2);
        }
        
        .bot-name {
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        
        .bot-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 0.9em;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
        }
        
        .health-bar, .food-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .health-fill, .food-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .health-fill {
            background: linear-gradient(90deg, #f44336, #ff9800, #4CAF50);
        }
        
        .food-fill {
            background: linear-gradient(90deg, #f44336, #ff9800, #4CAF50);
        }
        
        .command-section {
            grid-column: 1 / -1;
            text-align: center;
        }
        
        .command-input {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            justify-content: center;
            align-items: center;
        }
        
        .command-input input {
            padding: 12px 20px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 16px;
            width: 400px;
            backdrop-filter: blur(10px);
        }
        
        .command-input input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .command-input button {
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        
        .command-input button:hover {
            transform: translateY(-2px);
        }
        
        .world-map {
            grid-column: 1 / -1;
            text-align: center;
        }
        
        .map-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .map-grid {
            display: inline-grid;
            gap: 2px;
            margin: 10px 0;
        }
        
        .map-cell {
            width: 20px;
            height: 20px;
            background: #333;
            border-radius: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: white;
        }
        
        .map-cell.grass { background: #7cb342; }
        .map-cell.stone { background: #757575; }
        .map-cell.dirt { background: #8d6e63; }
        .map-cell.tree { background: #4e342e; }
        .map-cell.water { background: #42a5f5; }
        
        .status-indicators {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin: 20px 0;
        }
        
        .status-indicator {
            text-align: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            min-width: 120px;
        }
        
        .status-number {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .status-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .command-history {
            grid-column: 1 / -1;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .command-item {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #4CAF50;
        }
        
        .command-item.error {
            border-left-color: #f44336;
        }
        
        .command-item.processing {
            border-left-color: #ff9800;
        }
        
        .command-time {
            font-size: 0.8em;
            opacity: 0.7;
            margin-bottom: 5px;
        }
        
        .command-text {
            font-weight: bold;
        }
        
        .command-status {
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .refresh-button {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 20px;
            color: white;
            cursor: pointer;
            backdrop-filter: blur(10px);
        }
        
        .refresh-button:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                padding: 10px;
            }
            
            .command-input input {
                width: 250px;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Bot Vision Commander</h1>
        <p>Real-time Minecraft Bot Monitoring & Command Center</p>
    </div>
    
    <button class="refresh-button" onclick="refreshData()">🔄 Refresh</button>
    
    <div class="dashboard">
        <div class="panel">
            <h2>📊 Bot Status</h2>
            <div class="bot-grid" id="botGrid">
                <!-- Bot cards will be populated here -->
            </div>
        </div>
        
        <div class="panel">
            <h2>🌍 World Overview</h2>
            <div class="status-indicators">
                <div class="status-indicator">
                    <div class="status-number" id="totalBots">0</div>
                    <div class="status-label">Active Bots</div>
                </div>
                <div class="status-indicator">
                    <div class="status-number" id="totalBlocks">0</div>
                    <div class="status-label">Block Types</div>
                </div>
                <div class="status-indicator">
                    <div class="status-number" id="totalEntities">0</div>
                    <div class="status-label">Entity Types</div>
                </div>
            </div>
            <div class="world-map">
                <h3>World Map (Top View)</h3>
                <div class="map-container">
                    <div class="map-grid" id="worldMap">
                        <!-- World map will be populated here -->
                    </div>
                </div>
            </div>
        </div>
        
        <div class="panel command-section">
            <h2>💬 Live Commands</h2>
            <div class="command-input">
                <input type="text" id="commandInput" placeholder="Type your command here... (e.g., 'Bot1, mine iron ore')" />
                <button onclick="sendCommand()">🚀 Send Command</button>
            </div>
            <p style="opacity: 0.8; margin-top: 10px;">
                Examples: "Bot1, mine iron ore" | "All bots, collect wood" | "Bot2, go to 100 64 200"
            </p>
        </div>
        
        <div class="panel command-history">
            <h2>📝 Command History</h2>
            <div id="commandHistory">
                <!-- Command history will be populated here -->
            </div>
        </div>
    </div>
    
    <script>
        let botData = {};
        let worldData = {};
        let commandHistory = [];
        
        // Initialize the dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            setInterval(refreshData, 5000); // Refresh every 5 seconds
            
            // Enter key support for command input
            document.getElementById('commandInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendCommand();
                }
            });
        });
        
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    botData = data.bot_status || {};
                    worldData = data.world_overview || {};
                    updateDashboard();
                })
                .catch(error => console.error('Error fetching status:', error));
            
            fetch('/api/commands')
                .then(response => response.json())
                .then(data => {
                    commandHistory = data.commands || [];
                    updateCommandHistory();
                })
                .catch(error => console.error('Error fetching commands:', error));
        }
        
        function updateDashboard() {
            updateBotGrid();
            updateWorldOverview();
            updateWorldMap();
        }
        
        function updateBotGrid() {
            const botGrid = document.getElementById('botGrid');
            botGrid.innerHTML = '';
            
            Object.entries(botData).forEach(([botName, botInfo]) => {
                const botCard = document.createElement('div');
                botCard.className = 'bot-card';
                
                // Determine card class based on health
                if (botInfo.health < 10) botCard.classList.add('critical');
                else if (botInfo.health < 15) botCard.classList.add('warning');
                
                const healthPercent = (botInfo.health / 20) * 100;
                const foodPercent = (botInfo.food / 20) * 100;
                
                botCard.innerHTML = `
                    <div class="bot-name">${botName}</div>
                    <div class="bot-stats">
                        <div class="stat">
                            <span>Position:</span>
                            <span>${botInfo.position[0].toFixed(0)}, ${botInfo.position[1].toFixed(0)}, ${botInfo.position[2].toFixed(0)}</span>
                        </div>
                        <div class="stat">
                            <span>State:</span>
                            <span>${botInfo.state}</span>
                        </div>
                        <div class="stat">
                            <span>Health:</span>
                            <span>${botInfo.health.toFixed(1)}/20</span>
                        </div>
                        <div class="stat">
                            <span>Food:</span>
                            <span>${botInfo.food.toFixed(1)}/20</span>
                        </div>
                        <div class="stat">
                            <span>Nearby Blocks:</span>
                            <span>${botInfo.nearby_blocks}</span>
                        </div>
                        <div class="stat">
                            <span>Nearby Entities:</span>
                            <span>${botInfo.nearby_entities}</span>
                        </div>
                    </div>
                    <div class="health-bar">
                        <div class="health-fill" style="width: ${healthPercent}%"></div>
                    </div>
                    <div class="food-bar">
                        <div class="food-fill" style="width: ${foodPercent}%"></div>
                    </div>
                `;
                
                botGrid.appendChild(botCard);
            });
        }
        
        function updateWorldOverview() {
            document.getElementById('totalBots').textContent = Object.keys(botData).length;
            document.getElementById('totalBlocks').textContent = worldData.block_types ? worldData.block_types.length : 0;
            document.getElementById('totalEntities').textContent = worldData.entity_types ? worldData.entity_types.length : 0;
        }
        
        function updateWorldMap() {
            const worldMap = document.getElementById('worldMap');
            worldMap.innerHTML = '';
            
            // Create a simple 20x20 grid representation
            const gridSize = 20;
            for (let z = 0; z < gridSize; z++) {
                for (let x = 0; x < gridSize; x++) {
                    const cell = document.createElement('div');
                    cell.className = 'map-cell';
                    
                    // Simple terrain generation for demo
                    const terrainType = getTerrainType(x, z);
                    cell.classList.add(terrainType);
                    cell.textContent = terrainType[0].toUpperCase();
                    
                    worldMap.appendChild(cell);
                }
            }
        }
        
        function getTerrainType(x, z) {
            // Simple terrain generation
            const noise = Math.sin(x * 0.1) + Math.sin(z * 0.1);
            if (noise > 0.5) return 'grass';
            else if (noise > 0) return 'stone';
            else return 'dirt';
        }
        
        function updateCommandHistory() {
            const commandHistoryDiv = document.getElementById('commandHistory');
            commandHistoryDiv.innerHTML = '';
            
            commandHistory.slice(-10).reverse().forEach(cmd => {
                const commandItem = document.createElement('div');
                commandItem.className = 'command-item';
                
                if (cmd.status === 'error') commandItem.classList.add('error');
                else if (cmd.status === 'processing') commandItem.classList.add('processing');
                
                const time = new Date(cmd.timestamp).toLocaleTimeString();
                
                commandItem.innerHTML = `
                    <div class="command-time">${time}</div>
                    <div class="command-text">${cmd.command}</div>
                    <div class="command-status">Status: ${cmd.status}</div>
                `;
                
                commandHistoryDiv.appendChild(commandItem);
            });
        }
        
        function sendCommand() {
            const commandInput = document.getElementById('commandInput');
            const command = commandInput.value.trim();
            
            if (!command) return;
            
            // Add to local history immediately
            const newCommand = {
                timestamp: new Date().toISOString(),
                command: command,
                status: 'processing'
            };
            commandHistory.push(newCommand);
            updateCommandHistory();
            
            // Send to server
            fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update command status
                    newCommand.status = 'completed';
                    showNotification('✅ Command executed successfully!', 'success');
                } else {
                    newCommand.status = 'error';
                    showNotification('❌ Command failed: ' + data.error, 'error');
                }
                updateCommandHistory();
            })
            .catch(error => {
                newCommand.status = 'error';
                updateCommandHistory();
                showNotification('❌ Command failed: ' + error.message, 'error');
            });
            
            commandInput.value = '';
        }
        
        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                padding: 15px 25px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                animation: slideDown 0.3s ease;
                background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideDown {
                from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
"""

class BotVisionWebHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, commander=None, **kwargs):
        self.commander = commander
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            status_data = self.commander.get_bot_vision_summary()
            self.wfile.write(json.dumps(status_data).encode())
            
        elif self.path == '/api/commands':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            commands_data = {"commands": self.commander.command_history}
            self.wfile.write(json.dumps(commands_data).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            command_data = json.loads(post_data.decode('utf-8'))
            
            # Process command
            result = self.commander.process_live_command(command_data['command'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP request logging
        pass

class BotVisionWebServer:
    def __init__(self, commander, host='localhost', port=8080):
        self.commander = commander
        self.host = host
        self.port = port
        self.server = None
        
    def start(self):
        """Start the web server"""
        # Create custom handler class with commander instance
        handler_class = type('CustomHandler', (BotVisionWebHandler,), {
            '__init__': lambda self, *args, **kwargs: BotVisionWebHandler.__init__(self, *args, commander=self.commander, **kwargs)
        })
        
        self.server = HTTPServer((self.host, self.port), handler_class)
        
        print(f"🌐 Web server started at http://{self.host}:{self.port}")
        print(f"📱 Open your web browser and navigate to the URL above")
        print(f"🔄 The dashboard will automatically refresh every 5 seconds")
        print(f"🛑 Press Ctrl+C to stop the server\n")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down web server...")
            self.stop()
    
    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("✅ Web server stopped.")

def main():
    """Main function to run the web-based bot vision commander"""
    print("🚀 Starting Bot Vision Web Commander...")
    
    # Create commander instance
    commander = BotBrain() # Assuming BotBrain is the correct class for the commander
    
    # Start background updates
    commander.is_running = True
    update_thread = threading.Thread(target=commander._background_updates, daemon=True)
    update_thread.start()
    
    # Start web server
    web_server = BotVisionWebServer(commander)
    
    try:
        web_server.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        commander.is_running = False
        web_server.stop()
        print("✅ Bot Vision Web Commander stopped.")

if __name__ == "__main__":
    main()