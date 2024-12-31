from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from typing import Dict, Optional
import json

load_dotenv()

class RiskCalculatorTool(BaseTool):
    """
    Tool for calculating position sizes and managing risk parameters.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    max_position_size_pct: float = Field(
        default=5.0,
        description="Maximum position size as percentage of portfolio"
    )
    
    max_daily_trades: int = Field(
        default=10,
        description="Maximum number of trades per day"
    )
    
    max_daily_drawdown_pct: float = Field(
        default=3.0,
        description="Maximum daily drawdown percentage"
    )
    
    risk_per_trade_pct: float = Field(
        default=1.0,
        description="Risk percentage per trade"
    )
    
    daily_trades: int = Field(
        default=0,
        description="Current number of trades today"
    )
    
    daily_pnl: float = Field(
        default=0.0,
        description="Current daily PnL"
    )
    
    open_positions: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Dictionary of open positions"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.open_positions = {}
    
    def validate_trade(self, symbol: str, entry_price: float, stop_loss: Optional[float] = None) -> Dict:
        """Validate a trade against risk parameters."""
        try:
            # Check daily trade limit
            if self.daily_trades >= self.max_daily_trades:
                return {
                    "valid": False,
                    "reason": "Daily trade limit reached",
                    "position_size": 0
                }
            
            # Check daily drawdown
            if abs(self.daily_pnl) > self.max_daily_drawdown_pct:
                return {
                    "valid": False,
                    "reason": "Daily drawdown limit reached",
                    "position_size": 0
                }
            
            # Calculate position size
            position_size = self._calculate_position_size(entry_price, stop_loss)
            
            return {
                "valid": True,
                "position_size": position_size,
                "risk_amount": position_size * self.risk_per_trade_pct / 100
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Error validating trade: {str(e)}",
                "position_size": 0
            }
    
    def _calculate_position_size(self, entry_price: float, stop_loss: Optional[float] = None) -> float:
        """Calculate position size based on risk parameters."""
        # This is a simplified calculation
        # In practice, you would need to consider:
        # - Account balance
        # - Current market conditions
        # - Stop loss levels
        # - Asset volatility
        
        # For now, return a fixed percentage of max position size
        return entry_price * (self.max_position_size_pct / 100)
    
    def update_position(self, symbol: str, pnl: float):
        """Update position PnL and risk metrics."""
        self.daily_pnl += pnl
        self.daily_trades += 1
        
        if symbol in self.open_positions:
            self.open_positions[symbol]["pnl"] = pnl
    
    def run(self):
        """
        Main execution method for the tool.
        This tool is primarily used through its validate_trade method.
        """
        return "Risk calculator initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = RiskCalculatorTool(
        max_position_size_pct=5.0,
        max_daily_trades=10,
        max_daily_drawdown_pct=3.0,
        risk_per_trade_pct=1.0
    )
    
    # Test trade validation
    result = tool.validate_trade(
        symbol="SOL/USD",
        entry_price=100.0,
        stop_loss=95.0
    )
    
    print(json.dumps(result, indent=2)) 