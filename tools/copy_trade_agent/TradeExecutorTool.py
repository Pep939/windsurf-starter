from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.transaction import Transaction
from solders.instruction import Instruction
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address
from typing import Dict, Optional
import base58
import json

load_dotenv()

class TradeExecutorTool(BaseTool):
    """
    Tool for executing trades on Solana DEXs.
    Implements slippage protection and integrates with risk management parameters.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    wallet_keypair: str = Field(
        ...,
        description="Base58 encoded private key for the trading wallet"
    )
    
    max_slippage: float = Field(
        default=1.0,
        description="Maximum allowed slippage percentage"
    )
    
    default_dex: str = Field(
        default="raydium",
        description="Default DEX to use for trades (raydium/orca/serum)"
    )
    
    client: Optional[AsyncClient] = Field(
        default=None,
        description="Solana RPC client"
    )
    
    keypair: Optional[Keypair] = Field(
        default=None,
        description="Solana keypair for signing transactions"
    )
    
    risk_manager: Optional[object] = Field(
        default=None,
        description="Risk management interface"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.client:
            self.client = AsyncClient(os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com'))
        self.keypair = Keypair.from_bytes(base58.b58decode(self.wallet_keypair))
        self.risk_manager = None
    
    def set_risk_manager(self, risk_manager):
        """Set the risk management interface."""
        self.risk_manager = risk_manager
    
    def _check_risk_parameters(self, trade_params: Dict) -> bool:
        """Validate trade against risk management parameters."""
        if not self.risk_manager:
            return True
            
        # Check position size
        if not self.risk_manager.validate_position_size(trade_params["amount"]):
            return False
            
        # Check daily limit
        if not self.risk_manager.check_daily_limit():
            return False
            
        return True
    
    async def _get_token_account(self, token_mint: str) -> str:
        """Get or create associated token account."""
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            ata = get_associated_token_address(
                owner=self.keypair.pubkey(),
                mint=token_mint_pubkey
            )
            return str(ata)
        except Exception as e:
            print(f"Error getting token account: {e}")
            return None
    
    async def _build_swap_transaction(self, 
                                    input_token: str,
                                    output_token: str,
                                    amount: float,
                                    min_output_amount: float) -> Optional[Transaction]:
        """Build a swap transaction based on the selected DEX."""
        try:
            if self.default_dex == "raydium":
                return await self._build_raydium_swap(
                    input_token,
                    output_token,
                    amount,
                    min_output_amount
                )
            elif self.default_dex == "orca":
                return await self._build_orca_swap(
                    input_token,
                    output_token,
                    amount,
                    min_output_amount
                )
            else:
                raise ValueError(f"Unsupported DEX: {self.default_dex}")
        except Exception as e:
            print(f"Error building swap transaction: {e}")
            return None
    
    async def _build_raydium_swap(self, 
                                 input_token: str,
                                 output_token: str,
                                 amount: float,
                                 min_output_amount: float) -> Transaction:
        """Build a Raydium swap transaction."""
        # Implementation for Raydium swap
        # This is a placeholder - implement actual Raydium swap logic
        raise NotImplementedError("Raydium swap not implemented")
    
    async def _build_orca_swap(self,
                              input_token: str,
                              output_token: str,
                              amount: float,
                              min_output_amount: float) -> Transaction:
        """Build an Orca swap transaction."""
        # Implementation for Orca swap
        # This is a placeholder - implement actual Orca swap logic
        raise NotImplementedError("Orca swap not implemented")
    
    async def execute_trade(self,
                          input_token: str,
                          output_token: str,
                          amount: float,
                          price_impact: float = None) -> Dict:
        """
        Execute a trade with the given parameters.
        Returns transaction details or error information.
        """
        try:
            # Check risk parameters
            trade_params = {
                "amount": amount,
                "input_token": input_token,
                "output_token": output_token
            }
            
            if not self._check_risk_parameters(trade_params):
                return {
                    "success": False,
                    "error": "Trade rejected by risk management"
                }
            
            # Calculate minimum output amount based on slippage
            min_output_amount = amount * (1 - self.max_slippage / 100)
            
            # Build and send transaction
            transaction = await self._build_swap_transaction(
                input_token,
                output_token,
                amount,
                min_output_amount
            )
            
            if not transaction:
                return {
                    "success": False,
                    "error": "Failed to build transaction"
                }
            
            # Sign and send transaction
            opts = TxOpts(skip_preflight=True)
            result = await self.client.send_transaction(
                transaction,
                self.keypair,
                opts=opts
            )
            
            return {
                "success": True,
                "signature": result["result"],
                "input_token": input_token,
                "output_token": output_token,
                "amount": amount,
                "min_output_amount": min_output_amount
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self):
        """
        Main execution method for the tool.
        This tool is primarily used through its execute_trade method.
        """
        return "Trade executor initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = TradeExecutorTool(
        wallet_keypair="ExampleBase58PrivateKey",
        max_slippage=1.0,
        default_dex="raydium"
    )
    
    # Example trade execution
    import asyncio
    
    async def test_trade():
        result = await tool.execute_trade(
            input_token="SOL",
            output_token="USDC",
            amount=0.1
        )
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_trade()) 