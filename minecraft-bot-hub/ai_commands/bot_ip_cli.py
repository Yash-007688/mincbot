#!/usr/bin/env python3
"""
Bot IP Manager CLI - Command Line Interface
Provides easy control over bot IP rotation and management
"""

import argparse
import json
import sys
import time
from pathlib import Path
from bot_ip_manager import BotIPManager

class BotIPCLI:
    """Command Line Interface for Bot IP Manager"""
    
    def __init__(self):
        self.ip_manager = None
        self.setup_parser()
    
    def setup_parser(self):
        """Setup command line argument parser"""
        self.parser = argparse.ArgumentParser(
            description="Bot IP Manager CLI - Control bot IP rotation and management",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python bot_ip_cli.py status                    # Show all bot statuses
  python bot_ip_cli.py rotate --bot alpha       # Force rotate specific bot
  python bot_ip_cli.py rotate --all             # Force rotate all bots
  python bot_ip_cli.py config --bot beta        # Show bot configuration
  python bot_ip_cli.py test --bot gamma         # Test bot connection
  python bot_ip_cli.py security                 # Show security report
  python bot_ip_cli.py stats                    # Show connection statistics
  python bot_ip_cli.py monitor                  # Monitor in real-time
            """
        )
        
        # Add subcommands
        subparsers = self.parser.add_subparsers(dest='command', help='Available commands')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show bot statuses')
        status_parser.add_argument('--bot', help='Show status for specific bot')
        status_parser.add_argument('--json', action='store_true', help='Output in JSON format')
        
        # Rotate command
        rotate_parser = subparsers.add_parser('rotate', help='Rotate bot IPs')
        rotate_parser.add_argument('--bot', help='Rotate specific bot')
        rotate_parser.add_argument('--all', action='store_true', help='Rotate all bots')
        rotate_parser.add_argument('--force', action='store_true', help='Force immediate rotation')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Manage bot configuration')
        config_parser.add_argument('--bot', help='Show config for specific bot')
        config_parser.add_argument('--set', nargs=3, metavar=('BOT', 'KEY', 'VALUE'), help='Set configuration value')
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Test bot connections')
        test_parser.add_argument('--bot', help='Test specific bot')
        test_parser.add_argument('--all', action='store_true', help='Test all bots')
        
        # Security command
        security_parser = subparsers.add_parser('security', help='Show security information')
        security_parser.add_argument('--detailed', action='store_true', help='Show detailed security report')
        
        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show connection statistics')
        stats_parser.add_argument('--json', action='store_true', help='Output in JSON format')
        
        # Monitor command
        monitor_parser = subparsers.add_parser('monitor', help='Monitor bots in real-time')
        monitor_parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
        monitor_parser.add_argument('--duration', type=int, help='Monitor duration in seconds')
        
        # Proxy command
        proxy_parser = subparsers.add_parser('proxy', help='Manage proxy settings')
        proxy_parser.add_argument('--refresh', action='store_true', help='Refresh proxy lists')
        proxy_parser.add_argument('--status', action='store_true', help='Show proxy status')
        
        # VPN command
        vpn_parser = subparsers.add_parser('vpn', help='Manage VPN settings')
        vpn_parser.add_argument('--status', action='store_true', help='Show VPN status')
        vpn_parser.add_argument('--rotate', help='Rotate VPN for specific bot')
    
    def initialize_manager(self):
        """Initialize the Bot IP Manager"""
        try:
            self.ip_manager = BotIPManager()
            return True
        except Exception as e:
            print(f"Error initializing Bot IP Manager: {e}")
            return False
    
    def run(self):
        """Run the CLI"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        # Initialize manager
        if not self.initialize_manager():
            sys.exit(1)
        
        try:
            # Execute command
            if args.command == 'status':
                self.cmd_status(args)
            elif args.command == 'rotate':
                self.cmd_rotate(args)
            elif args.command == 'config':
                self.cmd_config(args)
            elif args.command == 'test':
                self.cmd_test(args)
            elif args.command == 'security':
                self.cmd_security(args)
            elif args.command == 'stats':
                self.cmd_stats(args)
            elif args.command == 'monitor':
                self.cmd_monitor(args)
            elif args.command == 'proxy':
                self.cmd_proxy(args)
            elif args.command == 'vpn':
                self.cmd_vpn(args)
            else:
                print(f"Unknown command: {args.command}")
                self.parser.print_help()
        
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.ip_manager:
                self.ip_manager.cleanup()
    
    def cmd_status(self, args):
        """Handle status command"""
        if args.bot:
            # Show status for specific bot
            status = self.ip_manager.get_bot_ip(args.bot)
            if status:
                if args.json:
                    print(json.dumps(status, indent=2))
                else:
                    self.print_bot_status(status)
            else:
                print(f"Bot {args.bot} not found")
        else:
            # Show status for all bots
            all_status = self.ip_manager.get_all_bot_ips()
            if args.json:
                print(json.dumps(all_status, indent=2))
            else:
                print("=== Bot Status Overview ===")
                for bot_id, status in all_status.items():
                    if status:
                        print(f"\n--- {bot_id.upper()} ---")
                        self.print_bot_status(status)
    
    def print_bot_status(self, status):
        """Print bot status in a formatted way"""
        print(f"Bot ID: {status['bot_id']}")
        print(f"Current IP: {status['ip']}:{status['port']}")
        print(f"Last Rotation: {status['last_rotation']}")
        print(f"Next Rotation: {status['next_rotation']}")
        print(f"Proxy Enabled: {'Yes' if status['proxy_enabled'] else 'No'}")
        print(f"VPN Enabled: {'Yes' if status['vpn_enabled'] else 'No'}")
        print(f"Stealth Mode: {'Yes' if status['stealth_mode'] else 'No'}")
        print(f"IP History Count: {status['ip_history_count']}")
    
    def cmd_rotate(self, args):
        """Handle rotate command"""
        if args.all:
            print("Rotating all bot IPs...")
            self.ip_manager.force_rotate_all_bots()
            print("All bot IPs rotated successfully")
        elif args.bot:
            print(f"Rotating IP for bot {args.bot}...")
            self.ip_manager.rotate_bot_ip(args.bot)
            print(f"Bot {args.bot} IP rotated successfully")
        else:
            print("Please specify --bot <bot_id> or --all")
    
    def cmd_config(self, args):
        """Handle config command"""
        if args.set:
            bot_id, key, value = args.set
            print(f"Setting {key} = {value} for bot {bot_id}...")
            success = self.ip_manager.update_bot_config(bot_id, **{key: value})
            if success:
                print("Configuration updated successfully")
            else:
                print("Failed to update configuration")
        elif args.bot:
            # Show configuration for specific bot
            bot_config = self.ip_manager.bot_configs.get(args.bot)
            if bot_config:
                print(f"=== Configuration for {args.bot.upper()} ===")
                print(f"Rotation Interval: {bot_config.rotation_interval}s")
                print(f"Proxy Enabled: {bot_config.proxy_enabled}")
                print(f"VPN Enabled: {bot_config.vpn_enabled}")
                print(f"Stealth Mode: {bot_config.stealth_mode}")
                print(f"Proxy Count: {len(bot_config.proxy_list)}")
                print(f"VPN Endpoints: {len(bot_config.vpn_endpoints)}")
            else:
                print(f"Bot {args.bot} not found")
        else:
            print("Please specify --bot <bot_id> or --set <bot> <key> <value>")
    
    def cmd_test(self, args):
        """Handle test command"""
        if args.all:
            print("Testing all bot connections...")
            for bot_id in self.ip_manager.bot_configs:
                result = self.ip_manager.test_connection(bot_id)
                print(f"\n--- {bot_id.upper()} ---")
                if 'error' in result:
                    print(f"Error: {result['error']}")
                else:
                    print(f"IP: {result['ip']}:{result['port']}")
                    print(f"Connection: {result['connection_test']}")
                    print(f"Timestamp: {result['timestamp']}")
        elif args.bot:
            print(f"Testing connection for bot {args.bot}...")
            result = self.ip_manager.test_connection(args.bot)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"IP: {result['ip']}:{result['port']}")
                print(f"Connection: {result['connection_test']}")
                print(f"Timestamp: {result['timestamp']}")
        else:
            print("Please specify --bot <bot_id> or --all")
    
    def cmd_security(self, args):
        """Handle security command"""
        report = self.ip_manager.get_security_report()
        
        if args.detailed:
            print(json.dumps(report, indent=2))
        else:
            print("=== Security Report ===")
            print(f"Timestamp: {report['timestamp']}")
            print("\nSecurity Features:")
            for feature, enabled in report['security_features'].items():
                print(f"  {feature}: {'✓' if enabled else '✗'}")
            
            print("\nTracking Prevention:")
            for method, enabled in report['tracking_prevention'].items():
                print(f"  {method}: {'✓' if enabled else '✗'}")
            
            print("\nRotation Statistics:")
            for bot_id, stats in report['rotation_stats'].items():
                print(f"  {bot_id}: {stats['total_rotations']} rotations")
    
    def cmd_stats(self, args):
        """Handle stats command"""
        stats = self.ip_manager.get_connection_stats()
        
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("=== Connection Statistics ===")
            print(f"Total Bots: {stats['total_bots']}")
            print(f"Active Connections: {stats['active_connections']}")
            print(f"Available IPs: {stats['available_ips']}")
            print(f"Used IPs: {stats['used_ips']}")
            print(f"Total IPs: {stats['total_ips']}")
            print(f"Last Regeneration: {stats['last_regeneration']}")
    
    def cmd_monitor(self, args):
        """Handle monitor command"""
        print(f"Monitoring bots (update interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        
        start_time = time.time()
        try:
            while True:
                # Clear screen (works on most terminals)
                print("\033[2J\033[H", end="")
                
                print(f"=== Bot Monitor (Interval: {args.interval}s) ===")
                print(f"Time: {time.strftime('%H:%M:%S')}")
                
                # Show current status
                all_status = self.ip_manager.get_all_bot_ips()
                for bot_id, status in all_status.items():
                    if status:
                        print(f"\n{bot_id.upper()}: {status['ip']}:{status['port']}")
                        print(f"  Next rotation: {status['next_rotation']}")
                        print(f"  Proxy: {'✓' if status['proxy_enabled'] else '✗'}")
                        print(f"  VPN: {'✓' if status['vpn_enabled'] else '✗'}")
                
                # Check if duration exceeded
                if args.duration and (time.time() - start_time) > args.duration:
                    break
                
                time.sleep(args.interval)
        
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    
    def cmd_proxy(self, args):
        """Handle proxy command"""
        if args.refresh:
            print("Refreshing proxy lists...")
            self.ip_manager.load_proxy_lists()
            print("Proxy lists refreshed")
        elif args.status:
            print("=== Proxy Status ===")
            for bot_id, bot_config in self.ip_manager.bot_configs.items():
                if bot_config.proxy_enabled:
                    print(f"{bot_id}: {len(bot_config.proxy_list)} proxies available")
                else:
                    print(f"{bot_id}: Proxies disabled")
        else:
            print("Please specify --refresh or --status")
    
    def cmd_vpn(self, args):
        """Handle VPN command"""
        if args.status:
            print("=== VPN Status ===")
            for bot_id, bot_config in self.ip_manager.bot_configs.items():
                if bot_config.vpn_enabled:
                    print(f"{bot_id}: {len(bot_config.vpn_endpoints)} VPN endpoints")
                else:
                    print(f"{bot_id}: VPN disabled")
        elif args.rotate:
            print(f"Rotating VPN for bot {args.rotate}...")
            # This would require additional VPN rotation logic
            print("VPN rotation not yet implemented")
        else:
            print("Please specify --status or --rotate <bot_id>")

def main():
    """Main entry point"""
    cli = BotIPCLI()
    cli.run()

if __name__ == "__main__":
    main()