from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from typing import List, Dict, Optional, Callable
import asyncio
import websockets
import json

load_dotenv()

class WalletMonitorTool(BaseTool):
    """
    Tool for monitoring wallet transactions in real-time on Solana.
    Filters transactions based on size and token whitelist.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    target_wallets: List[str] = Field(
        ...,
        description="List of wallet addresses to monitor"
    )
    
    min_transaction_size: float = Field(
        default=0.1,
        description="Minimum transaction size in SOL to consider"
    )
    
    token_whitelist: Optional[List[str]] = Field(
        default=None,
        description="Optional list of token addresses to monitor"
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
        if not self.client:
            self.client = AsyncClient(os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com'))
        if not self.ws_url:
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
    
    async def _process_transaction(self, notification: Dict) -> Optional[Dict]:
        """Process and filter incoming transaction notifications."""
        try:
            # Extract transaction data
            tx_data = notification.get("result", {}).get("value", {})
            
            # Check transaction size
            if float(tx_data.get("lamports", 0)) / 1e9 < self.min_transaction_size:
                return None
            
            # Check token whitelist if specified
            if self.token_whitelist:
                token_address = tx_data.get("tokenAddress")
                if not token_address or token_address not in self.token_whitelist:
                    return None
            
            # Determine transaction type
            tx_type = self._determine_transaction_type(tx_data)
            
            return {
                "type": tx_type,
                "wallet": tx_data.get("owner"),
                "amount": float(tx_data.get("lamports", 0)) / 1e9,
                "token": tx_data.get("tokenAddress"),
                "signature": tx_data.get("signature"),
                "timestamp": tx_data.get("blockTime")
            }
            
        except Exception as e:
            print(f"Error processing transaction: {e}")
            return None
    
    def _determine_transaction_type(self, tx_data: Dict) -> str:
        """Determine the type of transaction (swap, transfer, etc.)."""
        # This is a simplified implementation
        # In practice, you would need to analyze the instruction data
        program_id = tx_data.get("programId", "")
        
        if program_id == "11111111111111111111111111111111":
            return "transfer"
        elif program_id in ["9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin", "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1"]:
            return "swap"
        else:
            return "unknown"
    
    def add_transaction_handler(self, handler: Callable[[Dict], None]):
        """Add a callback function to handle processed transactions."""
        self.transaction_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start monitoring specified wallets and process notifications."""
        if not await self._connect():
            return False
        
        try:
            # Subscribe to all target wallets
            for wallet in self.target_wallets:
                await self._subscribe_account(wallet)
            
            # Process incoming notifications
            async for msg in self.ws_client:
                msg_data = json.loads(msg)
                if msg_data.get("method") == "accountNotification":
                    tx = await self._process_transaction(msg_data)
                    if tx:
                        # Notify all handlers
                        for handler in self.transaction_handlers:
                            handler(tx)
                            
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
        return "Wallet monitor initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = WalletMonitorTool(
        target_wallets=["ExampleWalletAddress"],
        min_transaction_size=0.1
    )
    
    def print_transaction(tx):
        print(json.dumps(tx, indent=2))
    
    tool.add_transaction_handler(print_transaction)
    
    # Run the monitoring loop
    asyncio.run(tool.start_monitoring()) 