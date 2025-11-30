try:
    from deluge_client import DelugeRPCClient
except ImportError:
    DelugeRPCClient = None
    print("⚠️ deluge-client not found. Torrent features will be simulated.")

class DelugeManager:
    """
    Manager for interacting with Deluge Daemon.
    """
    def __init__(self, host='127.0.0.1', port=58846, username='', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.connected = False

    def connect(self):
        """Connect to Deluge daemon."""
        if not DelugeRPCClient:
            return False
            
        try:
            self.client = DelugeRPCClient(self.host, self.port, self.username, self.password)
            self.client.connect()
            self.connected = True
            print("✅ Connected to Deluge Daemon")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Deluge: {e}")
            self.connected = False
            return False

    def add_magnet(self, magnet_link):
        """
        Add a magnet link to Deluge.
        
        Returns:
            str: Torrent ID if successful, None otherwise.
        """
        if not self.connected:
            if not self.connect():
                print("⚠️ Simulating magnet add (No Deluge connection)")
                return "SIMULATED_TORRENT_ID"
        
        try:
            torrent_id = self.client.core.add_torrent_magnet(magnet_link, {})
            # torrent_id is bytes in some versions, decode if needed
            if isinstance(torrent_id, bytes):
                torrent_id = torrent_id.decode('utf-8')
            print(f"⬇️ Added torrent: {torrent_id}")
            return torrent_id
        except Exception as e:
            print(f"❌ Error adding magnet: {e}")
            return None

    def get_torrent_status(self, torrent_id):
        """
        Get status of a specific torrent.
        
        Returns:
            dict: Status dict (progress, state, etc.)
        """
        if not self.connected or torrent_id == "SIMULATED_TORRENT_ID":
            # Simulation
            return {"progress": 50.0, "state": "Downloading", "name": "Simulated Anime"}
            
        try:
            # Keys we want
            keys = ["name", "state", "progress", "eta", "download_payload_rate"]
            status = self.client.core.get_torrent_status(torrent_id, keys)
            
            # Decode bytes keys/values if necessary
            decoded_status = {}
            for k, v in status.items():
                key = k.decode('utf-8') if isinstance(k, bytes) else k
                val = v.decode('utf-8') if isinstance(v, bytes) else v
                decoded_status[key] = val
                
            return decoded_status
        except Exception as e:
            print(f"❌ Error getting torrent status: {e}")
            return None
