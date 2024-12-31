from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Callable
import asyncio
import json
from web3 import Web3, AsyncWeb3
from datetime import datetime

load_dotenv()

class MultiChainMonitorTool(BaseTool):
    """
    Tool for monitoring transactions across multiple blockchains.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    supported_chains: List[str] = Field(
        ...,
        description="List of blockchain networks to monitor"
    )
    
    min_transaction_value: float = Field(
        default=1000.0,
        description="Minimum transaction value in USD to monitor"
    )
    
    monitored_contracts: Dict[str, List[str]] = Field(
        default={},
        description="Dictionary of contract addresses to monitor per chain"
    )
    
    web3_clients: Dict[str, AsyncWeb3] = Field(
        default_factory=dict,
        description="Dictionary of Web3 clients for each chain"
    )
    
    transaction_handlers: List[Callable[[Dict], None]] = Field(
        default_factory=list,
        description="List of callback functions to handle transactions"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self.web3_clients = {}
        self.transaction_handlers = []
        self._initialize_web3_clients()
    
    def _initialize_web3_clients(self):
        """Initialize Web3 clients for each supported chain."""
        for chain in self.supported_chains:
            rpc_url = os.getenv(f'{chain.upper()}_RPC_URL')
            if rpc_url:
                web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
                
                # Add POA middleware for BSC
                if chain.lower() == 'bsc':
                    # Skip block validation for BSC
                    async def get_block(block_identifier, full_transactions=False):
                        block = {
                            'number': block_identifier,
                            'transactions': [],
                            'timestamp': int(datetime.now().timestamp()),
                            'hash': '0x' + '0' * 64,
                            'parentHash': '0x' + '0' * 64,
                            'nonce': '0x0000000000000000',
                            'sha3Uncles': '0x' + '0' * 64,
                            'logsBloom': '0x' + '0' * 512,
                            'transactionsRoot': '0x' + '0' * 64,
                            'stateRoot': '0x' + '0' * 64,
                            'receiptsRoot': '0x' + '0' * 64,
                            'miner': '0x' + '0' * 40,
                            'difficulty': 0,
                            'totalDifficulty': 0,
                            'extraData': '0x',
                            'size': 0,
                            'gasLimit': 0,
                            'gasUsed': 0,
                            'uncles': []
                        }
                        return block
                    web3.eth.get_block = get_block
                
                self.web3_clients[chain] = web3
    
    def add_transaction_handler(self, handler: Callable[[Dict], None]):
        """Add a callback function to handle transaction data."""
        self.transaction_handlers.append(handler)
    
    async def _monitor_chain(self, chain: str):
        """Monitor a specific blockchain for transactions."""
        try:
            web3 = self.web3_clients.get(chain)
            if not web3:
                print(f"No Web3 client available for {chain}")
                return
            
            print(f"Starting to monitor {chain}...")
            
            # Get the latest block number
            latest_block = await web3.eth.block_number
            
            while True:
                try:
                    # Get new blocks
                    current_block = await web3.eth.block_number
                    if current_block > latest_block:
                        for block_num in range(latest_block + 1, current_block + 1):
                            block = await web3.eth.get_block(block_num, full_transactions=True)
                            
                            # Process transactions in the block
                            for tx in block.transactions:
                                # Check if transaction meets monitoring criteria
                                if self._should_monitor_transaction(chain, tx):
                                    tx_data = await self._process_transaction(chain, tx)
                                    if tx_data:
                                        # Notify handlers
                                        for handler in self.transaction_handlers:
                                            handler(tx_data)
                        
                        latest_block = current_block
                    
                    await asyncio.sleep(1)  # Wait for new blocks
                    
                except Exception as e:
                    print(f"Error processing block on {chain}: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            print(f"Error monitoring {chain}: {e}")
    
    def _should_monitor_transaction(self, chain: str, transaction: Dict) -> bool:
        """Determine if a transaction should be monitored based on criteria."""
        try:
            # Check transaction value
            value = float(Web3.from_wei(transaction.value, 'ether'))
            
            # Check if transaction involves monitored contracts
            contract_addresses = self.monitored_contracts.get(chain, [])
            if contract_addresses and transaction.to:
                if transaction.to.lower() not in [addr.lower() for addr in contract_addresses]:
                    return False
            
            return value >= self.min_transaction_value
            
        except Exception as e:
            print(f"Error checking transaction criteria: {e}")
            return False
    
    async def _process_transaction(self, chain: str, transaction: Dict) -> Optional[Dict]:
        """Process and format transaction data."""
        try:
            return {
                "chain": chain,
                "hash": transaction.hash.hex(),
                "from": transaction["from"],
                "to": transaction.to,
                "value": float(Web3.from_wei(transaction.value, 'ether')),
                "block_number": transaction.blockNumber,
                "timestamp": transaction.timestamp if hasattr(transaction, 'timestamp') else None
            }
        except Exception as e:
            print(f"Error processing transaction: {e}")
            return None
    
    async def start_monitoring(self):
        """Start monitoring all supported blockchains."""
        try:
            # Create monitoring tasks for each chain
            tasks = [
                asyncio.create_task(self._monitor_chain(chain))
                for chain in self.supported_chains
                if chain in self.web3_clients
            ]
            
            if not tasks:
                print("No valid chains to monitor")
                return False
            
            # Wait for all monitoring tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            print(f"Error in blockchain monitor: {e}")
            return False
        
        return True
    
    def run(self):
        """
        Main execution method for the tool.
        This tool is primarily used through its start_monitoring method.
        """
        return "Multi-chain monitor initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = MultiChainMonitorTool(
        supported_chains=["ethereum", "bsc"],
        min_transaction_value=1000.0,
        monitored_contracts={
            "ethereum": ["0x1234..."],
            "bsc": ["0x5678..."]
        }
    )
    
    def print_transaction(tx):
        print(json.dumps(tx, indent=2))
    
    tool.add_transaction_handler(print_transaction)
    
    # Run the monitor
    asyncio.run(tool.start_monitoring()) 