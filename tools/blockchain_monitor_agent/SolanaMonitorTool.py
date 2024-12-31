from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from typing import List, Dict, Optional, Callable
import asyncio
import websockets
import json

load_dotenv()

class SolanaMonitorTool(BaseTool):
    """
    Tool for monitoring Solana blockchain transactions.
    Provides real-time transaction data to other agents.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    tracked_wallets: List[str] = Field(
        ...,
        description="List of wallet addresses to monitor"
    )
    
    client: Optional[AsyncClient] = Field(
        default=None,
        description="Solana RPC client"
    )
    
    ws_url: Optional[str] = Field(
        default=None,
        description="WebSocket URL for Solana RPC"
    )
    
    ws_client: Optional[websockets.WebSocketClientProtocol] = Field(
        default=None,
        description="WebSocket client"
    )
    
    transaction_handlers: List[Callable[[Dict], None]] = Field(
        default_factory=list,
        description="List of callback functions to handle transactions"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self.client = AsyncClient(os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com'))
        self.ws_url = os.getenv('SOLANA_WS_URL', 'wss://api.mainnet-beta.solana.com')
        self.ws_client = None
        self.transaction_handlers = []
    
    async def _connect(self):
        """Establish WebSocket connection."""
        try:
            if not self.ws_client:
                self.ws_client = await websockets.connect(self.ws_url)
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")
            return False
        return True
    
    async def _subscribe_account(self, pubkey: str):
        """Subscribe to account notifications for a specific wallet."""
        try:
            subscribe_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "accountSubscribe",
                "params": [
                    pubkey,
                    {"encoding": "jsonParsed", "commitment": "confirmed"}
                ]
            }
            await self.ws_client.send(json.dumps(subscribe_message))
        except Exception as e:
            print(f"Error subscribing to account {pubkey}: {e}")
    
    async def _fetch_transaction_data(self, signature: str) -> Optional[Dict]:
        """Fetch detailed transaction data."""
        try:
            tx = await self.client.get_transaction(
                signature,
                encoding="jsonParsed"
            )
            return tx["result"]
        except Exception as e:
            print(f"Error fetching transaction data: {e}")
            return None
    
    def add_transaction_handler(self, handler: Callable[[Dict], None]):
        """Add a callback function to handle transaction data."""
        self.transaction_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start monitoring the Solana blockchain."""
        if not await self._connect():
            return False
        
        try:
            # Subscribe to all tracked wallets
            for wallet in self.tracked_wallets:
                await self._subscribe_account(wallet)
            
            # Process incoming notifications
            async for msg in self.ws_client:
                msg_data = json.loads(msg)
                if msg_data.get("method") == "accountNotification":
                    signature = msg_data.get("params", {}).get("result", {}).get("signature")
                    if signature:
                        tx_data = await self._fetch_transaction_data(signature)
                        if tx_data:
                            # Notify all handlers
                            for handler in self.transaction_handlers:
                                handler(tx_data)
                                
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            return False
        finally:
            if self.ws_client:
                await self.ws_client.close()
        
        return True
    
    def run(self):
        """
        Main execution method for the tool.
        This tool is primarily used through its start_monitoring method.
        """
        return "Solana monitor initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = SolanaMonitorTool(
        tracked_wallets=["ExampleWalletAddress"]
    )
    
    def print_transaction(tx):
        print(json.dumps(tx, indent=2))
    
    tool.add_transaction_handler(print_transaction)
    
    # Run the monitoring loop
    asyncio.run(tool.start_monitoring()) 