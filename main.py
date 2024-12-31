import os
import asyncio
from dotenv import load_dotenv
import json
from datetime import datetime
from typing import Dict, Any

# Import agent tools
from tools.copy_trade_agent.WalletMonitorTool import WalletMonitorTool
from tools.copy_trade_agent.TradeExecutorTool import TradeExecutorTool
from tools.market_sentinel_agent.TokenScannerTool import TokenScannerTool
from tools.market_sentinel_agent.SentimentAnalyzerTool import SentimentAnalyzerTool
from tools.risk_management_agent.RiskCalculatorTool import RiskCalculatorTool
from tools.risk_management_agent.StopLossManagerTool import StopLossManagerTool
from tools.blockchain_monitor_agent.SolanaMonitorTool import SolanaMonitorTool

load_dotenv()

# Debug: Print environment variables
print("Environment variables:")
print(f"TRADING_WALLET_KEYPAIR: {os.getenv('TRADING_WALLET_KEYPAIR')}")
print(f"TARGET_WALLETS: {os.getenv('TARGET_WALLETS')}")
print(f"MIN_TRANSACTION_SIZE: {os.getenv('MIN_TRANSACTION_SIZE')}")

class CryptoTradingAgency:
    """
    Main agency class that coordinates all trading agents.
    """
    
    def __init__(self):
        # Initialize tools
        self.wallet_monitor = WalletMonitorTool(
            target_wallets=json.loads(os.getenv('TARGET_WALLETS', '[]')),
            min_transaction_size=float(os.getenv('MIN_TRANSACTION_SIZE', '0.1'))
        )
        
        self.trade_executor = TradeExecutorTool(
            wallet_keypair=os.getenv('TRADING_WALLET_KEYPAIR'),
            max_slippage=float(os.getenv('MAX_SLIPPAGE', '1.0')),
            default_dex=os.getenv('DEFAULT_DEX', 'raydium')
        )
        
        self.token_scanner = TokenScannerTool(
            target_dexs=["raydium", "orca"],
            min_liquidity=float(os.getenv('MIN_LIQUIDITY', '10000')),
            volume_change_threshold=float(os.getenv('VOLUME_CHANGE_THRESHOLD', '200')),
            price_change_threshold=float(os.getenv('PRICE_CHANGE_THRESHOLD', '5'))
        )
        
        self.sentiment_analyzer = SentimentAnalyzerTool(
            target_tokens=json.loads(os.getenv('TARGET_TOKENS', '["SOL", "BTC", "ETH"]')),
            sentiment_threshold=float(os.getenv('SENTIMENT_THRESHOLD', '0.2')),
            min_mentions=int(os.getenv('MIN_MENTIONS', '10'))
        )
        
        self.risk_calculator = RiskCalculatorTool(
            max_position_size_pct=float(os.getenv('MAX_POSITION_SIZE_PCT', '5.0')),
            max_daily_trades=int(os.getenv('MAX_DAILY_TRADES', '10')),
            max_daily_drawdown_pct=float(os.getenv('MAX_DAILY_DRAWDOWN_PCT', '3.0')),
            risk_per_trade_pct=float(os.getenv('RISK_PER_TRADE_PCT', '1.0'))
        )
        
        self.stop_loss_manager = StopLossManagerTool(
            default_stop_loss_pct=float(os.getenv('DEFAULT_STOP_LOSS_PCT', '2.0')),
            default_take_profit_pct=float(os.getenv('DEFAULT_TAKE_PROFIT_PCT', '4.0')),
            trailing_stop_activation_pct=float(os.getenv('TRAILING_STOP_ACTIVATION_PCT', '2.0')),
            trailing_stop_distance_pct=float(os.getenv('TRAILING_STOP_DISTANCE_PCT', '1.5'))
        )
        
        self.solana_monitor = SolanaMonitorTool(
            tracked_wallets=json.loads(os.getenv('MONITORED_PROGRAMS', '[]')),
            min_transaction_size=float(os.getenv('MIN_SOL_TRANSACTION_SIZE', '1000.0'))
        )
        
        # Set up handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up event handlers between agents."""
        # Copy Trade Agent handlers
        self.wallet_monitor.add_transaction_handler(self._handle_wallet_transaction)
        
        # Market Sentinel Agent handlers
        self.token_scanner.add_alert_handler(self._handle_market_alert)
        self.sentiment_analyzer.add_transaction_handler(self._handle_sentiment_alert)
        
        # Blockchain Monitor Agent handlers
        self.solana_monitor.add_transaction_handler(self._handle_blockchain_transaction)
    
    async def _handle_wallet_transaction(self, transaction: Dict[str, Any]):
        """Handle transactions detected by the wallet monitor."""
        try:
            # Validate trade with risk management
            validation = self.risk_calculator.validate_trade(
                symbol=transaction.get("symbol"),
                entry_price=transaction.get("price"),
                stop_loss=transaction.get("stop_loss")
            )
            
            if validation["valid"]:
                # Execute trade
                result = await self.trade_executor.execute_trade(
                    input_token=transaction.get("input_token"),
                    output_token=transaction.get("output_token"),
                    amount=validation["position_size"]
                )
                
                if result["success"]:
                    # Initialize stop-loss management
                    self.stop_loss_manager.initialize_position(
                        symbol=transaction.get("symbol"),
                        entry_price=transaction.get("price"),
                        position_size=validation["position_size"]
                    )
                
                print(f"Trade execution result: {json.dumps(result, indent=2)}")
            else:
                print(f"Trade validation failed: {validation['reason']}")
                
        except Exception as e:
            print(f"Error handling wallet transaction: {e}")
    
    async def _handle_market_alert(self, alert: Dict[str, Any]):
        """Handle market alerts from the token scanner."""
        try:
            print(f"Market alert received: {json.dumps(alert, indent=2)}")
            
            # Update risk parameters based on market conditions
            if alert["type"] == "volatility_alert":
                # Adjust risk parameters
                pass
            
        except Exception as e:
            print(f"Error handling market alert: {e}")
    
    async def _handle_sentiment_alert(self, alert: Dict[str, Any]):
        """Handle sentiment alerts from the analyzer."""
        try:
            print(f"Sentiment alert received: {json.dumps(alert, indent=2)}")
            
            # Adjust trading parameters based on sentiment
            if abs(alert["sentiment"]["score"]) > 0.5:
                # Update trading strategy
                pass
            
        except Exception as e:
            print(f"Error handling sentiment alert: {e}")
    
    async def _handle_blockchain_transaction(self, transaction: Dict[str, Any]):
        """Handle blockchain transactions from monitors."""
        try:
            print(f"Blockchain transaction detected: {json.dumps(transaction, indent=2)}")
            
            # Update market data based on blockchain activity
            if transaction.get("type") == "token_transfer":
                # Process token transfer
                pass
            elif transaction.get("type") == "dex_trade":
                # Process DEX trade
                pass
            
        except Exception as e:
            print(f"Error handling blockchain transaction: {e}")
    
    async def start(self):
        """Start all agents and begin monitoring."""
        try:
            print("Starting Crypto Trading Agency...")
            
            # Start all monitoring tasks
            tasks = [
                asyncio.create_task(self.wallet_monitor.start_monitoring()),
                asyncio.create_task(self.token_scanner.start_scanning()),
                asyncio.create_task(self.sentiment_analyzer.start_analysis()),
                asyncio.create_task(self.solana_monitor.start_monitoring())
            ]
            
            # Wait for all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            print(f"Error starting agency: {e}")
            raise

if __name__ == "__main__":
    # Create and start the agency
    agency = CryptoTradingAgency()
    
    try:
        asyncio.run(agency.start())
    except KeyboardInterrupt:
        print("\nShutting down agency...")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise