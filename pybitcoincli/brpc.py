import requests
import json

class BitcoinRPC:
    def __init__(self, user, password, host="127.0.0.1", port=8332, keepalive=False):
        """
        Initialize the RPC client.
        :param user: RPC username
        :param password: RPC password
        :param host: IP or hostname of the Bitcoin node
        :param port: RPC port (default 8332 on mainnet)
        :param keepalive: If True, use a requests.Session() to keep connection open
        """
        self.url = f"http://{host}:{port}"
        self.auth = (user, password)
        self.keepalive = keepalive
        
        if self.keepalive:
            # Create a persistent Session if keepalive is requested
            self.session = requests.Session()
            self.session.auth = self.auth
        else:
            self.session = None

    def call(self, method, *params):
        """
        Generic JSON-RPC caller.
        Usage: rpc.call("getblockcount") or rpc.call("getblockhash", 100)
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": list(params)
        }
        try:
            if self.keepalive and self.session:
                # Reuse the session if keepalive is enabled
                response = self.session.post(self.url, json=payload)
            else:
                # Otherwise, create a one-off request each time
                response = requests.post(self.url, auth=self.auth, json=payload)
            
            response.raise_for_status()  # Raise an error if we got an HTTP 4xx/5xx
            response_json = response.json()
            
            if "error" in response_json and response_json["error"] is not None:
                raise Exception(f"RPC error: {response_json['error']}")
            return response_json["result"]
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {e}")