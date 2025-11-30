"""
Deluge client configuration.
Default credentials are 'deluge' for both username and password.
"""
import os
import json
from pathlib import Path

# Default configuration
DELUGE_CONFIG = {
    'host': '127.0.0.1',
    'port': 58846,  # Default Deluge daemon port
    'username': 'deluge',
    'password': 'deluge',
    'auth_level': 10  # Admin level
}

def get_deluge_client():
    """Return a configured Deluge client instance with proper authentication."""
    try:
        from deluge_client import DelugeRPCClient
        
        print(f"DEBUG AUTH: Trying to connect as User: {DELUGE_CONFIG['username']}, Pass: {DELUGE_CONFIG['password']}")
        
        # Create client with default config
        client = DelugeRPCClient(
            host=DELUGE_CONFIG['host'],
            port=DELUGE_CONFIG['port'],
            username=DELUGE_CONFIG['username'],
            password=DELUGE_CONFIG['password']
        )
        
        # Test connection
        if client.connect():
            print("✅ Successfully connected to Deluge")
            return client
        else:
            print("❌ Failed to connect to Deluge")
            return None
            
    except Exception as e:
        print(f"❌ Deluge connection error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure Deluge daemon is running")
        print("2. Check if the Web UI is accessible at http://localhost:8112")
        print("3. Verify the username and password in the auth file")
        print("4. Check if the port 58846 is not blocked by firewall")
        return None
