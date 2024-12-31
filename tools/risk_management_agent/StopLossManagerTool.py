from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from typing import Dict, Optional
import json

load_dotenv()

class StopLossManagerTool(BaseTool):
    """
    Tool for managing stop-loss and take-profit orders.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    default_stop_loss_pct: float = Field(
        default=2.0,
        description="Default stop-loss percentage"
    )
    
    default_take_profit_pct: float = Field(
        default=4.0,
        description="Default take-profit percentage"
    )
    
    trailing_stop_activation_pct: float = Field(
        default=2.0,
        description="Percentage gain required to activate trailing stop"
    )
    
    trailing_stop_distance_pct: float = Field(
        default=1.5,
        description="Trailing stop distance percentage"
    )
    
    positions: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Dictionary of positions with their stop-loss and take-profit levels"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self.positions = {}
    
    def initialize_position(self, symbol: str, entry_price: float, position_size: float) -> Dict:
        """Initialize stop-loss and take-profit levels for a new position."""
        try:
            stop_loss = entry_price * (1 - self.default_stop_loss_pct / 100)
            take_profit = entry_price * (1 + self.default_take_profit_pct / 100)
            
            position = {
                "symbol": symbol,
                "entry_price": entry_price,
                "position_size": position_size,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "trailing_stop": None,
                "highest_price": entry_price
            }
            
            self.positions[symbol] = position
            return position
            
        except Exception as e:
            print(f"Error initializing position: {e}")
            return None
    
    def update_position(self, symbol: str, current_price: float) -> Optional[Dict]:
        """Update position and check for stop-loss/take-profit triggers."""
        try:
            if symbol not in self.positions:
                return None
            
            position = self.positions[symbol]
            
            # Update highest price
            if current_price > position["highest_price"]:
                position["highest_price"] = current_price
                
                # Check if trailing stop should be activated
                price_gain_pct = (current_price - position["entry_price"]) / position["entry_price"] * 100
                if price_gain_pct >= self.trailing_stop_activation_pct:
                    position["trailing_stop"] = current_price * (1 - self.trailing_stop_distance_pct / 100)
            
            # Check for stop-loss trigger
            if current_price <= position["stop_loss"]:
                return {
                    "action": "close",
                    "reason": "stop_loss",
                    "symbol": symbol,
                    "price": current_price
                }
            
            # Check for take-profit trigger
            if current_price >= position["take_profit"]:
                return {
                    "action": "close",
                    "reason": "take_profit",
                    "symbol": symbol,
                    "price": current_price
                }
            
            # Check trailing stop
            if position["trailing_stop"] and current_price <= position["trailing_stop"]:
                return {
                    "action": "close",
                    "reason": "trailing_stop",
                    "symbol": symbol,
                    "price": current_price
                }
            
            return {
                "action": "hold",
                "symbol": symbol,
                "current_price": current_price,
                "stop_loss": position["stop_loss"],
                "take_profit": position["take_profit"],
                "trailing_stop": position["trailing_stop"]
            }
            
        except Exception as e:
            print(f"Error updating position: {e}")
            return None
    
    def close_position(self, symbol: str):
        """Close a position and remove it from tracking."""
        if symbol in self.positions:
            del self.positions[symbol]
    
    def run(self):
        """
        Main execution method for the tool.
        This tool is primarily used through its position management methods.
        """
        return "Stop loss manager initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = StopLossManagerTool(
        default_stop_loss_pct=2.0,
        default_take_profit_pct=4.0,
        trailing_stop_activation_pct=2.0,
        trailing_stop_distance_pct=1.5
    )
    
    # Initialize a position
    position = tool.initialize_position(
        symbol="SOL/USD",
        entry_price=100.0,
        position_size=1.0
    )
    
    print("Initial position:", json.dumps(position, indent=2))
    
    # Test position update
    update = tool.update_position(
        symbol="SOL/USD",
        current_price=103.0
    )
    
    print("\nPosition update:", json.dumps(update, indent=2)) 