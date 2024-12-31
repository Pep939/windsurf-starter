from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Callable
import asyncio
import json

load_dotenv()

class TokenScannerTool(BaseTool):
    """
    Tool for scanning token activity across DEXs.
    Monitors price and volume movements.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    target_dexs: List[str] = Field(
        ...,
        description="List of DEXs to monitor"
    )
    
    min_liquidity: float = Field(
        default=10000,
        description="Minimum liquidity in USD"
    )
    
    volume_change_threshold: float = Field(
        default=200,
        description="Volume change percentage to trigger alert"
    )
    
    price_change_threshold: float = Field(
        default=5,
        description="Price change percentage to trigger alert"
    )
    
    alert_handlers: List[Callable[[Dict], None]] = Field(
        default_factory=list,
        description="List of callback functions to handle alerts"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self.alert_handlers = []
        
    def add_alert_handler(self, handler: Callable[[Dict], None]):
        """Add a callback function to handle alerts."""
        self.alert_handlers.append(handler)
    
    async def start_scanning(self):
        """Start scanning for token activity."""
        try:
            print("Token scanner started...")
            while True:
                # Placeholder for actual scanning logic
                await asyncio.sleep(60)  # Scan every minute
                
        except Exception as e:
            print(f"Error in token scanner: {e}")
            return False
        
        return True
    
    def run(self):
        """
        Main execution method for the tool.
        This tool is primarily used through its start_scanning method.
        """
        return "Token scanner initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = TokenScannerTool(
        target_dexs=["raydium", "orca"],
        min_liquidity=10000,
        volume_change_threshold=200,
        price_change_threshold=5
    )
    
    def print_alert(alert):
        print(json.dumps(alert, indent=2))
    
    tool.add_alert_handler(print_alert)
    
    # Run the scanner
    asyncio.run(tool.start_scanning()) 